import io
import types
import typing

import click
from flask import Flask
from werkzeug.routing import FloatConverter, BaseConverter, IntegerConverter, UUIDConverter, PathConverter, UnicodeConverter
from werkzeug.routing.rules import Rule

from .stubs import Response
from .ts_types import TSType, TSSimpleType, TSObject, TSRecord, TSUnion, TSArray, TSTuple, is_signal


type Type = typing.Any
type TypeTreeTuple = tuple[TypeTree, ...]
type TypeTreeDict = dict[str, TypeTree]
type TypeTree = Type | tuple[Type, TypeTreeTuple | TypeTreeDict]
type GenericParamValues = dict[typing.TypeVar, TypeTree]


class Logger(typing.Protocol):
    def info(self, text: str) -> None: ...
    def warn(self, text: str) -> None: ...
    def error(self, text: str) -> None: ...


class ClickLogger:
    @staticmethod
    def info(text: str) -> None:
        click.echo(f"Info: {text}")

    @staticmethod
    def warn(text: str) -> None:
        click.secho(f"Warning: {text}", fg="yellow")

    @staticmethod
    def error(text: str) -> None:
        click.secho(f"Error: {text}", fg="red")


def get_type_hints(tp: typing.Any) -> dict[str, typing.Any]:
    return getattr(tp, "__annotations__", {})


class FlaskAnnotationsParser:
    def __init__(self, app: Flask, rule: Rule, logger: Logger | None = None) -> None:
        self.app = app
        self.rule = rule
        self.logger = ClickLogger() if logger is None else logger

    @property
    def rule_name(self) -> str:
        return self.rule.endpoint.replace(".", "_")
    
    @property
    def rule_url(self) -> str:
        return "".join([
            (f"<{content}>" if arg else content) for arg, content in self.rule._trace
        ][1:])

    def parse_args_type(self) -> TSType | None:
        try:
            used_converters: dict[str, BaseConverter] = {
                arg: converter
                for arg, converter in 
                ((arg, self.rule._converters.get(arg, None)) for arg in self.rule.arguments)
                if converter is not None
            }
            types: list[tuple[str, TSType]] = [
                (arg, self._get_converter_type(arg, converter))
                for arg, converter in used_converters.items()
            ]

            return (
                TSObject([t[0] for t in types], [t[1] for t in types])
                if len(types) > 0
                else TSSimpleType("undefined")
            )

        except Exception as e:
            self.logger.error(f"couldn't parse argument types ({e})")
            return None
    
    def parse_return_type(self) -> TSType | None:
        try:
            function = self.app.view_functions[self.rule.endpoint]
            annotations = get_type_hints(function)

            if annotations is None or "return" not in annotations:
                return TSSimpleType("undefined")

            return_annotations = annotations["return"]
            route_return_annotations = self._get_route_annotations(return_annotations)

            tree = self._type_tree(route_return_annotations)
            return self._generate_ts_type(tree)

        except Exception as e:
            self.logger.error(f"couldn't parse return type ({e})")
            return None

    def _get_generic_param_values(self, tp: Type, generic_values: TypeTreeTuple | TypeTreeDict) -> GenericParamValues:
        values = generic_values if isinstance(generic_values, tuple) else generic_values.values()
        return {
            param: self._type_tree(value) for param, value in zip(tp.__type_params__, values)
        }

    def _unwrap_generic(self, tp: TypeTree, generic_param_values: GenericParamValues) -> TypeTreeTuple:
        if isinstance(tp, tuple):
            return (tp[0], tuple(self._unwrap_generic(inner_tp, generic_param_values) for inner_tp in tp[1]))
        args = typing.get_args(tp)
        if len(args) == 0:
            return generic_param_values[tp] if isinstance(tp, typing.TypeVar) else tp
        
        unwrapped_args = tuple(self._unwrap_generic(arg, generic_param_values) for arg in args)
        origin = typing.get_origin(tp)
        return (origin, unwrapped_args)
        

    def _unwrap_generics_in_alias(self, tp: Type, generic_values: TypeTreeTuple, variables: TypeTreeTuple) -> TypeTreeTuple:
        generic_params = self._get_generic_param_values(tp, generic_values)
        return tuple(
            self._unwrap_generic(variable, generic_params)
            for variable in variables
        )

    def _unwrap_generics_in_dict(self, tp: Type, generic_values: TypeTreeTuple) -> TypeTreeDict:
        generic_params = self._get_generic_param_values(tp, generic_values)
        return {
            key: (self._unwrap_generic(value, generic_params))
            for key, value in typing.get_type_hints(tp).items()
        }

    def _type_tree(self, tp: Type) -> TypeTree:
        if isinstance(tp, typing.TypeAliasType):
            # If `tp` is an alias, call this method on its value
            return self._type_tree(tp.__value__)
        
        origin = typing.get_origin(tp) or tp
        args = typing.get_args(tp)
        
        if isinstance(origin, typing.TypeAliasType):
            # If `tp` is a generic alias, call this method on its value, but keep generic args
            tree = self._type_tree(tp.__value__)
            if isinstance(tree, tuple):
                new_args = self._unwrap_generics_in_alias(origin, args, tree[1])
                origin = typing.get_origin(tree[0]) or tree[0]
                return (origin, new_args)
            return tree

        if typing.is_typeddict(origin):
            # If the type is a `TypedDict`, we return a dictionary with its
            # fields and corresponding types.
            new_args = self._unwrap_generics_in_dict(origin, args)
            return (
                tp,
                new_args,
            )

        if len(args) > 0:
            return (
                origin,
                tuple(self._type_tree(arg) for arg in args),  
            )
        return tp

    def _generate_ts_type_simple(self, python_type: typing.Any) -> TSType:
        type_string: str
        if python_type is str:
            type_string = "string"
        elif python_type is int or python_type is float:
            type_string = "number"
        elif python_type is bool:
            type_string = "boolean"
        elif python_type is None or python_type is type(None):
            type_string = "null"
        elif python_type is dict:
            type_string = "object"
        elif python_type is list or python_type is tuple:
            return TSArray(TSSimpleType("any"))
        elif python_type is typing.Any:
            type_string = "any"
        elif python_type is typing.Never:
            type_string = "never"
        elif python_type is ...:
            # Special signal value
            type_string = "..."
        else:
            self.logger.warn(
                f"can't convert '{getattr(python_type, '__name__', python_type)}' to a TypeScript equivalent, defaulting to 'any'"
            )
            type_string = "any"
        
        return TSSimpleType(type_string)

    def _generate_ts_dict(self, python_type: typing.Any, args: tuple[TSType, ...]) -> TSObject | TSRecord:
        key = args[0] if len(args) >= 1 else TSSimpleType("string")
        value = args[1] if len(args) >= 2 else TSSimpleType("any")

        if len(args) != 2:
            self.logger.error(
                f"invalid type annotation '{python_type}', defaulting to 'Record<{key.generate()}, {value.generate()}>'"
            )

        if typing.get_origin(key) is typing.Literal:
            key_args: tuple[str] = typing.get_args(key)
            return TSObject(key_args, [value for _ in key_args])
        return TSRecord(key, value)

    def _generate_ts_tuple_or_array(self, args: tuple[TSType, ...]) -> TSArray | TSTuple:
        if len(args) == 0:
            return TSArray(TSSimpleType("any"))
        if is_signal(args[-1]) and len(args) == 2:
            return TSArray(args[0])
        return TSTuple(args)

    def _generate_ts_typeddict(self, python_type: typing.Any, args: dict[str, TSType]) -> TSObject:
        origin = typing.get_origin(python_type) or python_type
        hints = get_type_hints(origin)
        keys = tuple(hints.keys())
        required = tuple(typing.get_origin(value) is not typing.NotRequired for value in hints.values())
        value_types = tuple(arg_value for arg_value in args.values())
        return TSObject(keys, value_types, required)

    def _generate_ts_type_composite(self, python_type: typing.Any, args: tuple[TSType, ...]) -> TSType:
        origin = typing.get_origin(python_type) or python_type
        if origin is dict:
            return self._generate_ts_dict(python_type, args)
        if origin is tuple:
            return self._generate_ts_tuple_or_array(args)
        if origin is list:
            return TSArray(args[0])
        if origin is types.UnionType or origin is typing.Union:
            return TSUnion(args)
        if origin is Response:
            assert len(args) == 1, "Invalid Response type"
            return args[0]
        self.logger.warn(
            f"can't convert '{getattr(origin, '__name__', origin)}' to a TypeScript equivalent, defaulting to 'unknown'"
        )
        return TSSimpleType("unknown")

    def _generate_ts_type(self, tree: TypeTree) -> TSType:
        if isinstance(tree, tuple):
            assert len(tree) == 2
            if isinstance(tree[-1], tuple):
                return self._generate_ts_type_composite(
                    tree[0], 
                    tuple(self._generate_ts_type(arg) for arg in tree[-1])
                )
            elif isinstance(tree[-1], dict):
                return self._generate_ts_typeddict(
                    tree[0],
                    {name: self._generate_ts_type(arg) for name, arg in tree[-1].items()}
                )
            assert False, "Invalid type"
        return self._generate_ts_type_simple(tree)

    def _get_route_annotations_from_tuple(self, tp: typing.Any) -> Type:
        args = typing.get_args(tp)
        return args[0]

    def _get_route_annotations(self, tp: typing.Any) -> Type:
        origin = typing.get_origin(tp) or tp
        if origin is tuple:
            return self._get_route_annotations_from_tuple(tp)
        return tp

    def _get_converter_type(self, arg: str, converter: BaseConverter) -> TSType:
        if isinstance(converter, FloatConverter) or isinstance(converter, IntegerConverter):
            return TSSimpleType("number")
        if isinstance(converter, UUIDConverter) or isinstance(converter, PathConverter) or isinstance(converter, UnicodeConverter):
            return TSSimpleType("string")

        # Custom converter, check to_python() annotations
        annotations = get_type_hints(converter.to_python)
        if annotations is None or "return" not in annotations:
            self.logger.warn(
                f"route '{self.rule.endpoint}', argument '{arg}': using non-standard"
                "converter without type annotations, defaulting to 'string'",
            )
            return TSSimpleType("string")
        
        return_annotations = annotations["return"]
        tree = self._type_tree(return_annotations)
        return self._generate_ts_type(tree)


class CodeWriter:
    def __init__(self, types_file: io.TextIOBase, api_file: io.TextIOBase, endpoint: str = "", stop_on_error: bool = False) -> None:
        self.types_file = types_file
        self.api_file = api_file
        self.endpoint = endpoint
        self.stop_on_error = stop_on_error

    def write(self, parsers: typing.Iterable[FlaskAnnotationsParser]) -> bool:
        error = False
        self._write_api_header()
        for parser in parsers:
            return_type = parser.parse_return_type()
            args_type = parser.parse_args_type()
            if return_type is None or args_type is None:
                error = True
                if self.stop_on_error:
                    return False
                continue
            self._write_api_function(parser.rule_name, parser.rule_url, args_type)
            self._write_types(parser.rule_name, return_type, args_type)
        return not error
    
    def _write_api_header(self) -> None:
        self.api_file.write("import * as types from \"./types\";\n\n")
        self.api_file.write(f'const BASE_ENDPOINT = "{self.endpoint}";\n\n')
        self.api_file.write(
            "function join(urlPart1: string, urlPart2: string) {\n"
            "    let url = urlPart1;\n"
            '    if (!url.endsWith("/") && !urlPart2.startsWith("/")) {\n'
            '        url += "/";\n'
            "    }\n"
            '    else if (url.endsWith("/") && urlPart2.startsWith("/")) {\n'
            '        url = url.substring(0, -1);\n'
            "    }\n"
            "    url += urlPart2;\n"
            "    return url;\n"
            "}\n\n"
        )

        self.api_file.write(
            "async function request(endpoint: string) {\n"
            "    const req = await fetch(join(BASE_ENDPOINT, endpoint));\n"
            "    if (!req.ok) throw Error(`Request failed with code ${req.status}.`);\n"
            "    const json = await req.json();\n"
            "    return json;\n"
            "}\n\n"
        )

        self.api_file.write(
            '// eslint-disable-next-line @typescript-eslint/no-explicit-any\n'
            'export function buildUrl(rule: string, params: Record<string, any>) {\n'
            '    return rule.replace(/<([a-zA-Z_]+[a-zA-Z_0-9]*)>/, (_, key) => {\n'
            '        return String(params[key]);\n'
            '    });\n'
            '}\n\n'
        )

    def _write_api_function(self, rule_name: str, rule_url: str, args_type: TSType) -> None:
        params = f"params: types.{rule_name}_ArgsType" if args_type != "undefined" else ""
        url_for_params = "params" if args_type != "undefined" else ""
        build_url = f'buildUrl("{rule_url}", params)' if args_type != "undefined" else f'"{rule_url}"'
        self.api_file.write(
            f"export function urlFor_{rule_name}({params}): string {{\n"
            f'    const endpoint = {build_url};\n'
            "    return endpoint;\n"
            "}\n\n"
        )
        self.api_file.write(
            f"export async function request_{rule_name}({params}): Promise<types.{rule_name}_ReturnType> {{\n"
            f"    const endpoint = urlFor_{rule_name}({url_for_params});\n"
            f"    return await request(endpoint);\n"
            "}\n\n"
        )

    def _write_types(self, rule_name: str, return_type: TSType, args_type: TSType) -> None:
        self.types_file.write(f"export type {rule_name}_ReturnType = {return_type.generate()};\n")
        self.types_file.write(f"export type {rule_name}_ArgsType = {args_type.generate()};\n\n")
