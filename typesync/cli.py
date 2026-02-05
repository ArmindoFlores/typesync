import os
import typing

import click
from flask import current_app
from flask.cli import AppGroup
from prettytable import PrettyTable
from werkzeug.routing.rules import Rule

from . import argument_types
from .codegen import CodeWriter, FlaskRouteTypeExtractor

if typing.TYPE_CHECKING:
    from .type_translators import Translator


cli = AppGroup("typesync")


@cli.command(help="Generate Typescript types based on Flask routes.")
@click.argument("out_dir", type=click.Path(file_okay=False, resolve_path=True))
@click.option("--endpoint", "-E", help="The base endpoint.", default="")
@click.option("--samefile", "-S", help="Write types and apis to the same file.")
@click.option(
    "--translator",
    "-t",
    help=(
        "Path to a python script containing a additional type translators. "
        "May be used multiple times."
    ),
    type=argument_types.TRANSLATOR_PLUGIN,
    multiple=True,
)
@click.option(
    "--translator-priority",
    help=("Set the priority of a translator.May be used multiple times."),
    type=argument_types.TRANSLATOR_PRIORITY,
    multiple=True,
)
@click.option(
    "--inference",
    "-i",
    is_flag=True,
    help="Whether to use inference when type annotations cannot be resolved.",
)
@click.option(
    "--inference-can-eval",
    is_flag=True,
    help=(
        "Whether eval() can be called during inference. WARNING: this will"
        " execute arbitrary code."
    ),
)
@click.option(
    "--types-file",
    help="Name of output file containing type definitions (defaults to 'types.ts').",
    default="types.ts",
)
@click.option(
    "--apis-file",
    help="Name of output file containing API functions (defaults to 'apis.ts').",
    default="apis.ts",
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
        "{uc} (UPPERCASE), "
        "{lc} (lowercase), "
        "{sc} (snake_case). "
        "Defaults to: '{pc}ReturnType'."
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
        "{uc} (UPPERCASE), "
        "{lc} (lowercase), "
        "{sc} (snake_case). "
        "Defaults to: '{pc}ArgsType'."
    ),
)
@click.option(
    "--function-name-format",
    default="{m_lc}{r_pc}",
    help=(
        "Format string used to generate function names from the route and HTTP method. "
        "Available placeholders are: "
        "{r_d} or {m_d} (default route name or HTTP method), "
        "{r_cc} or {m_cc} (camelCase), "
        "{r_pc} or {m_pc} (PascalCase), "
        "{r_uc} or {m_uc} (UPPERCASE), "
        "{r_lc} or {m_lc} (lowercase), "
        "{r_sc} or {m_sc} (snake_case). "
        "Defaults to: '{m_lc}{r_pc}'."
    ),
)
def generate(
    out_dir: str,
    endpoint: str,
    translator: tuple["Translator", ...],
    translator_priority: tuple[tuple[str, int], ...],
    inference: bool,
    inference_can_eval: bool,
    types_file: str,
    apis_file: str,
    return_type_format: str,
    args_type_format: str,
    function_name_format: str,
    samefile: str | None = None,
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
            FlaskRouteTypeExtractor(
                current_app,
                rule,
                translators=translator,
                translator_priorities=dict(translator_priority),
                inference_enabled=inference,
                inference_can_eval=inference_can_eval,
            )
            for rule in rules
        )
        if not result:
            click.secho("Errors occurred during file generation", fg="red")


@cli.command(help="Show available translators and their default priorities.")
def list_translators():
    translators = FlaskRouteTypeExtractor.default_translators()
    table = PrettyTable()
    table.field_names = ["ID", "Priority"]
    table.add_rows(
        [[translator.ID, translator.DEFAULT_PRIORITY] for translator in translators]
    )
    table.align["ID"] = "l"
    table.align["Priority"] = "r"
    print(table)
