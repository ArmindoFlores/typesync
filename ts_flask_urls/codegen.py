import io
import typing

import click
from flask import Flask
from werkzeug.routing import FloatConverter, BaseConverter, IntegerConverter, UUIDConverter, PathConverter, UnicodeConverter
from werkzeug.routing.rules import Rule

from .ts_types import TSType, TSSimpleType, TSObject
from .type_translators import TypeNode, to_type_node

if typing.TYPE_CHECKING:
    from .type_translators import Translator


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
    def __init__(self, app: Flask, rule: Rule, translators: tuple[typing.Type["Translator"]] | None = None, logger: Logger | None = None) -> None:
        self.app = app
        self.rule = rule
        self.logger = ClickLogger() if logger is None else logger
        self.translators = self._load_default_translators() if translators is None else translators

    @staticmethod
    def _load_default_translators() -> tuple[typing.Type["Translator"]]:
        from .type_translators import BaseTranslator, FlaskTranslator
        return (BaseTranslator, FlaskTranslator)

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
        
    def translate_type(self, type_: Type) -> TSType:
        def translate(node: TypeNode, generics: dict[str, TSType]) -> TSType:
            for translator in translators:
                r = translator.translate(node, generics)
                if r is not None:
                    return r
                
            self.logger.warn(
                f"can't translate '{getattr(node.origin, '__name__', node.origin)}' to a TypeScript equivalent, defaulting to 'any'"
            )
            return TSSimpleType("any")
        
        translators = [Translator(translate) for Translator in self.translators]
        node = to_type_node(type_)
        return translate(node, {})
    
    def parse_return_type(self) -> TSType | None:
        try:
            function = self.app.view_functions[self.rule.endpoint]
            annotations = get_type_hints(function)

            if annotations is None or "return" not in annotations:
                return TSSimpleType("undefined")

            return_annotations = annotations["return"]
            route_return_annotations = self._get_route_annotations(return_annotations)
            return self.translate_type(route_return_annotations)

        except Exception as e:
            self.logger.error(f"couldn't parse return type ({e})")
            return None

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
        return self.translate_type(return_annotations)


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
