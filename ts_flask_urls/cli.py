import os

import click
from flask import current_app
from flask.cli import AppGroup
from werkzeug.routing.rules import Rule

from .codegen import CodeWriter, FlaskRouteTypeExtractor


cli = AppGroup("ts-flask-urls")


@cli.command(help="Generate Typescript types based on Flask routes.")
@click.argument("out_dir", type=click.Path(file_okay=False, resolve_path=True))
@click.option("--endpoint", "-E", help="The base endpoint.", default="")
@click.option("--samefile", "-S", help="Write types and apis to the same file")
@click.option(
    "--types-file",
    help="Name of output file containing type definitions (defaults to 'types.ts')",
    default="types.ts"
)
@click.option(
    "--apis-file",
    help="Name of output file containing API functions (defaults to 'apis.ts')",
    default="apis.ts"
)
@click.option(
    "--return-type-format",
    default="{pc}ReturnType",
    help=(
        "Format string used to generate return type names from the route name. "
        "Available placeholders are: "
        "{d} (default route name), "
        "{cc} (camelCase), "
        "{pc} (PascalCase), "
        "{sc} (snake_case). "
        "Defaults to: '{pc}ReturnType'"
    ),
)
@click.option(
    "--args-type-format",
    default="{pc}ArgsType",
    help=(
        "Format string used to generate argument type names from the route name. "
        "Available placeholders are: "
        "{d} (default route name), "
        "{cc} (camelCase), "
        "{pc} (PascalCase), "
        "{sc} (snake_case). "
        "Defaults to: '{pc}ArgsType'"
    ),
)
@click.option(
    "--function-name-format",
    default="request{pc}",
    help=(
        "Format string used to generate function names from the route name. "
        "Available placeholders are: "
        "{d} (default route name), "
        "{cc} (camelCase), "
        "{pc} (PascalCase), "
        "{sc} (snake_case). "
        "Defaults to: 'request{pc}'"
    ),
)
def map_urls(
    out_dir: str,
    endpoint: str,
    types_file: str,
    apis_file: str,
    return_type_format: str,
    args_type_format: str,
    function_name_format: str,
    samefile: str | None = None
):
    rules: list[Rule] = list(current_app.url_map.iter_rules())

    os.makedirs(out_dir, exist_ok=True)

    with (
        open(os.path.join(out_dir, types_file), "w") as types_f,
        open(os.path.join(out_dir, apis_file), "w") as api_f,
    ):
        code_writer = CodeWriter(
            types_f,
            api_f,
            types_file,
            return_type_format,
            args_type_format,
            function_name_format,
            endpoint,
        )
        result = code_writer.write(
            FlaskRouteTypeExtractor(current_app, rule) for rule in rules
        )
        if not result:
            click.secho("Errors occurred during file generation", fg="red")
