import typing

import inflection

from typesync.ts_types import TSType, TSSimpleType

if typing.TYPE_CHECKING:
    from io import TextIOBase
    from typesync.misc import HTTPMethod
    from .extractor import RouteTypeExtractor


def make_rule_name_map(rule_name: str, prefix: str = "") -> dict[str, str]:
    return {
        prefix + "pc": inflection.camelize(rule_name, True),
        prefix + "cc": inflection.camelize(rule_name, False),
        prefix + "sc": inflection.underscore(rule_name),
        prefix + "uc": rule_name.replace("_", "").upper(),
        prefix + "lc": rule_name.replace("_", "").lower(),
        prefix + "d": rule_name,
    }


class TypesDict(typing.TypedDict):
    return_type: TSType
    args_type: TSType
    json_body_type: TSType


class CodeWriter:
    def __init__(
        self,
        types_file: "TextIOBase",
        api_file: "TextIOBase",
        types_file_name: str,
        return_type_format: str,
        params_type_format: str,
        function_name_format: str,
        endpoint: str = "",
        stop_on_error: bool = False,
    ) -> None:
        self.types_file = types_file
        self.api_file = api_file
        self.types_file_name = types_file_name.removesuffix(".ts")
        self.return_type_format = return_type_format
        self.params_type_format = params_type_format
        self.function_name_format = function_name_format
        self.endpoint = endpoint
        self.stop_on_error = stop_on_error

    def _api_function_name(self, rule_name: str, method: str) -> str:
        return self.function_name_format.format_map(
            {**make_rule_name_map(rule_name, "r_"), **make_rule_name_map(method, "m_")}
        )

    def _return_type_name(self, rule_name: str, method: str) -> str:
        return self.return_type_format.format_map(
            {**make_rule_name_map(rule_name, "r_"), **make_rule_name_map(method, "m_")}
        )

    def _params_type_name(self, rule_name: str, method: str) -> str:
        return self.params_type_format.format_map(
            {**make_rule_name_map(rule_name, "r_"), **make_rule_name_map(method, "m_")}
        )

    def _bundle_types_per_method(
        self,
        return_types: dict["HTTPMethod", TSType],
        args_types: dict["HTTPMethod", TSType],
        json_body_types: dict["HTTPMethod", TSType],
    ) -> dict["HTTPMethod", TypesDict]:
        methods = {*return_types.keys(), *args_types.keys(), *json_body_types.keys()}
        return {
            method: TypesDict(
                return_type=return_types.get(method, TSSimpleType("undefined")),
                args_type=args_types.get(method, TSSimpleType("undefined")),
                json_body_type=json_body_types.get(method, TSSimpleType("undefined")),
            )
            for method in sorted(methods)
        }

    def write(self, parsers: typing.Iterable["RouteTypeExtractor"]) -> bool:
        error = False
        self._write_types_header()
        self._write_api_header()
        names: list[str] = []
        endpoints_and_methods: dict[str, set[str]] = {}
        for parser in parsers:
            return_types = parser.parse_return_types()
            if parser.should_skip:
                continue
            args_types = parser.parse_args_types()
            json_body_types = parser.parse_json_body()

            types_per_method = self._bundle_types_per_method(
                return_types, args_types, json_body_types
            )

            for (
                method,
                return_type_name,
                params_type_name,
                has_args,
                has_json,
            ) in self._write_types(parser.rule_name, types_per_method):
                if method in endpoints_and_methods.get(parser.rule_name, set()):
                    continue
                endpoints_and_methods.setdefault(parser.rule_name, set()).add(method)
                names.append(
                    self._write_api_function(
                        parser.rule_name,
                        parser.rule_url,
                        method,
                        return_type_name,
                        params_type_name,
                        has_args,
                        has_json,
                    )
                )
        self._write_api_footer(names)
        return not error

    def _write_types_header(self) -> None:
        self.types_file.write(
            "export interface RequestArgs {\n"
            "    headers?: Record<string, string>;\n"
            "}\n\n"
        )
        self.types_file.write(
            "export interface RequestOptions extends RequestArgs {\n"
            "    method: string;\n"
            "    body?: unknown;\n"
            "}\n\n"
        )
        self.types_file.write(
            "export type RequestFunction = (\n"
            "    endpoint: string, options: RequestOptions\n"
            "// eslint-disable-next-line @typescript-eslint/no-explicit-any\n"
            ") => Promise<any>;"
            "\n\n"
        )

    def _write_api_header(self) -> None:
        self.api_file.write(f'import * as types from "./{self.types_file_name}";\n\n')
        self.api_file.write(
            "// eslint-disable-next-line @typescript-eslint/no-explicit-any\n"
            "export function buildUrl(rule: string, params: Record<string, any>) {\n"
            "    return rule.replace(/<([a-zA-Z_]+[a-zA-Z_0-9]*)>/, (_, key) => {\n"
            "        return String(params[key]);\n"
            "    });\n"
            "}\n\n",
        )
        self.api_file.write(
            "export function makeAPI(requestFn: types.RequestFunction) {\n"
        )

    def _write_api_footer(self, names: list[str]) -> None:
        self.api_file.write("    return {\n")
        for name in names:
            self.api_file.write(f"        {name},\n")
        self.api_file.write("    };\n")
        self.api_file.write("}\n")

    def _write_api_function(
        self,
        rule_name: str,
        rule_url: str,
        method: str,
        return_type_name: str,
        args_type_name: str,
        has_args: bool,
        has_json: bool,
    ) -> str:
        build_url = (
            f'buildUrl("{rule_url}", params.args)' if has_args else f'"{rule_url}"'
        )
        params = f"params: types.{args_type_name}"
        f_name = self._api_function_name(rule_name, method)
        self.api_file.write(
            f"    async function {f_name}({params}): Promise<types.{return_type_name}> {{\n"  # noqa: E501
            f"        const endpoint = {build_url};\n"
            "        return await requestFn(\n"
            "            endpoint,\n"
            '            {method: "' + method + '", ...params}\n'
            "        );\n"
            "    }\n\n",
        )
        return f_name

    def _write_types(
        self,
        rule_name: str,
        types_per_method: dict["HTTPMethod", TypesDict],
    ) -> typing.Generator[tuple[str, str, str, bool, bool], None, None]:
        for method, types in types_per_method.items():
            return_type_name = self._return_type_name(rule_name, method)
            generated_return_type = types["return_type"].generate(return_type_name)
            self.types_file.write(
                f"export type {return_type_name} = {generated_return_type};\n"
            )
            params_type_name = self._params_type_name(rule_name, method)
            optional_args = "?" if types["args_type"] == "undefined" else ""
            json_body_type = types["json_body_type"]
            optional_body = (
                "?" if json_body_type is None or json_body_type == "undefined" else ""
            )

            internal_args_name = f"_{rule_name}{method}Args"
            generated_args_type = types["args_type"].generate(internal_args_name)
            self.types_file.write(
                f"type {internal_args_name} = {generated_args_type};\n"
            )

            internal_body_name = f"_{rule_name}{method}Body"
            string_json_body_type = (
                "undefined"
                if types["json_body_type"] is None
                else types["json_body_type"].generate(internal_body_name)
            )
            self.types_file.write(
                f"type {internal_body_name} = {string_json_body_type};\n"
            )

            self.types_file.write(
                f"export interface {params_type_name} extends RequestArgs" + " {\n"
                f"    args{optional_args}: {internal_args_name};\n"
                f"    body{optional_body}: {internal_body_name};\n"
                "}\n\n"
            )

            yield (
                method,
                return_type_name,
                params_type_name,
                optional_args == "",
                optional_body == "",
            )
