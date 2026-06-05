import os

import click
from flask import current_app
from flask.cli import AppGroup
from prettytable import PrettyTable
from werkzeug.routing.rules import Rule

from . import argument_types, config
from .codegen import CodeWriter, RouteTypeExtractor


cli = AppGroup("typesync")


@cli.command(help="Generate Typescript types based on Flask routes.")
@click.argument(
    "out_dir", default=None, type=click.Path(file_okay=False, resolve_path=True)
)
@click.option("--endpoint", "-E", help="The base endpoint.", default="")
@click.option("--samefile", "-S", help="Write types and apis to the same file.")
@click.option(
    "--translator",
    "-t",
    "translators",
    help=(
        "Path to a python script containing an additional type translator, "
        "or name of a built-in one. "
        "May be used multiple times."
    ),
    type=argument_types.TRANSLATOR_PLUGIN,
    multiple=True,
)
@click.option(
    "--translator-priority",
    "translator_priorities",
    callback=lambda _ctx, _option, value: dict(value),
    help=(
        "Set the priority of a translator (TranslatorName:priority). "
        "May be used multiple times."
    ),
    type=argument_types.TRANSLATOR_PRIORITY,
    multiple=True,
)
@click.option(
    "--skip-unannotated",
    type=bool,
    default=True,
    help=(
        "Whether to skip code generation for routes whose annotations are not specified"
        " and could not be inferred. Defaults to True."
    ),
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
    default="{r_pc}{m_uc}ReturnType",
    help=(
        "Format string used to generate return type names from the route name. "
        "Available placeholders are: "
        "{r_d} or {m_d} (default route name or HTTP method), "
        "{r_cc} or {m_cc} (camelCase), "
        "{r_pc} or {m_pc} (PascalCase), "
        "{r_uc} or {m_uc} (UPPERCASE), "
        "{r_lc} or {m_lc} (lowercase), "
        "{r_sc} or {m_sc} (snake_case). "
        "Defaults to: '{r_pc}{m_uc}ReturnType'."
    ),
)
@click.option(
    "--args-type-format",
    default="{r_pc}{m_uc}ArgsType",
    help=(
        "Format string used to generate argument type names from the route name. "
        "Available placeholders are: "
        "{r_d} or {m_d} (default route name or HTTP method), "
        "{r_cc} or {m_cc} (camelCase), "
        "{r_pc} or {m_pc} (PascalCase), "
        "{r_uc} or {m_uc} (UPPERCASE), "
        "{r_lc} or {m_lc} (lowercase), "
        "{r_sc} or {m_sc} (snake_case). "
        "Defaults to: '{r_pc}{m_uc}ArgsType'."
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
@click.option(
    "--config",
    type=click.Path(dir_okay=False, resolve_path=True),
    help="A config file to be used in addition to the command line arguments.",
)
@click.pass_context
def generate(ctx: click.Context, **_):
    try:
        params = config.merge_config_params(ctx)
    except Exception as e:
        click.secho(f"Error: could not parse config file: {e!s}", fg="red")
        raise SystemExit(1) from None

    if params.out_dir is None:
        ctx.fail("Missing argument 'OUT_DIR'")

    rules: list[Rule] = sorted(
        current_app.url_map.iter_rules(), key=lambda rule: rule.endpoint
    )
    os.makedirs(params.out_dir, exist_ok=True)

    with (
        open(os.path.join(params.out_dir, params.types_file), "w") as types_f,
        open(os.path.join(params.out_dir, params.apis_file), "w") as api_f,
    ):
        code_writer = CodeWriter(
            types_f,
            api_f,
            params.types_file,
            params.return_type_format,
            params.args_type_format,
            params.function_name_format,
            params.endpoint,
        )
        result = code_writer.write(
            RouteTypeExtractor(
                current_app,
                rule,
                translators=params.translators,
                translator_priorities=params.translator_priorities,
                inference_enabled=params.inference,
                inference_can_eval=params.inference_can_eval,
                skip_unannotated=params.skip_unannotated,
            )
            for rule in rules
        )
        if not result:
            click.secho("Errors occurred during file generation", fg="red")


@cli.command(help="Show available translators and their default priorities.")
def list_translators():
    translators = RouteTypeExtractor.sort_translators(
        RouteTypeExtractor.all_translators(), {}
    )
    table = PrettyTable()
    table.field_names = ["ID", "Priority"]
    table.add_rows(
        [[translator.ID, translator.DEFAULT_PRIORITY] for translator in translators]
    )
    table.align["ID"] = "l"
    table.align["Priority"] = "r"
    print(table)
