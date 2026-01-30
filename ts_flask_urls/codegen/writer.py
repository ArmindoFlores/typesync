import typing

import inflection

if typing.TYPE_CHECKING:
    from io import TextIOBase
    from ts_flask_urls.ts_types import TSType
    from .extractor import FlaskRouteTypeExtractor


def make_rule_name_map(rule_name: str) -> dict[str, str]:
    return {
        "pc": inflection.camelize(rule_name, True),
        "cc": inflection.camelize(rule_name, False),
        "sc": inflection.underscore(rule_name),
        "d": rule_name,
    }


class CodeWriter:
    def __init__(
        self,
        types_file: "TextIOBase",
        api_file: "TextIOBase",
        types_file_name: str,
        return_type_format: str,
        args_type_format: str,
        function_name_format: str,
        endpoint: str = "",
        stop_on_error: bool = False,
    ) -> None:
        self.types_file = types_file
        self.api_file = api_file
        self.types_file_name = types_file_name.removesuffix(".ts")
        self.return_type_format = return_type_format
        self.args_type_format = args_type_format
        self.function_name_format = function_name_format
        self.endpoint = endpoint
        self.stop_on_error = stop_on_error

    def _api_function_name(self, rule_name: str) -> str:
        return self.function_name_format.format_map(
            make_rule_name_map(rule_name)
        )

    def _return_type_name(self, rule_name: str) -> str:
        return self.return_type_format.format_map(
            make_rule_name_map(rule_name)
        )

    def _args_type_name(self, rule_name: str) -> str:
        return self.args_type_format.format_map(
            make_rule_name_map(rule_name)
        )

    def write(self, parsers: typing.Iterable["FlaskRouteTypeExtractor"]) -> bool:
        error = False
        self._write_api_header()
        names = []
        for parser in parsers:
            return_type = parser.parse_return_type()
            args_type = parser.parse_args_type()
            if return_type is None or args_type is None:
                error = True
                if self.stop_on_error:
                    return False
                continue
            return_type_name, args_type_name = self._write_types(
                parser.rule_name, return_type, args_type
            )
            names.append(
                self._write_api_function(
                    parser.rule_name,
                    parser.rule_url,
                    args_type,
                    return_type_name,
                    args_type_name
                )
            )
        self._write_api_footer(names)
        return not error

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
            "// eslint-disable-next-line @typescript-eslint/no-explicit-any\n"
            "type RequestFunction = (endpoint: string) => Promise<any>;\n\n"
        )
        self.api_file.write(
            "export function makeAPI(requestFn: RequestFunction) {\n"
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
        args_type: "TSType",
        return_type_name: str,
        args_type_name: str
    ) -> str:
        params = (
            f"params: types.{args_type_name}" if args_type != "undefined" else ""
        )
        url_for_params = "params" if args_type != "undefined" else ""
        build_url = (
            f'buildUrl("{rule_url}", params)'
            if args_type != "undefined"
            else f'"{rule_url}"'
        )
        f_name = self._api_function_name(rule_name)
        self.api_file.write(
            f"    function urlFor_{rule_name}({params}): string {{\n"
            f"        const endpoint = {build_url};\n"
            "         return endpoint;\n"
            "    }\n\n",
        )
        self.api_file.write(
            f"    async function {f_name}({params}): Promise<types.{return_type_name}> {{\n"  # noqa: E501
            f"        const endpoint = urlFor_{rule_name}({url_for_params});\n"
            f"        return await requestFn(endpoint);\n"
            "    }\n\n",
        )
        return f_name

    def _write_types(
        self, rule_name: str, return_type: "TSType", args_type: "TSType"
    ) -> tuple[str, str]:
        return_type_name = self._return_type_name(rule_name)
        self.types_file.write(
            f"export type {return_type_name} = {return_type.generate(return_type_name)}"
            ";\n"
        )
        args_type_name = self._args_type_name(rule_name)
        self.types_file.write(
            f"export type {args_type_name} = {args_type.generate(args_type_name)};\n\n"
        )
        return return_type_name, args_type_name
