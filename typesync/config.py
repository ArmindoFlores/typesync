from argparse import Namespace
from collections.abc import Callable, Iterable
import json
import pathlib
import tomllib
from typing import Any

from click import Context
from click.core import ParameterSource
import yaml


def toml_parser(file: pathlib.Path) -> dict[str, Any]:
    with file.open("rb") as f:
        data = tomllib.load(f)
    if file.name == "pyproject.toml":
        # With pyproject, the configuration will be specified within
        # [tool.typesync]
        return data.get("tool", {}).get("typesync", {})
    return data


def json_parser(file: pathlib.Path) -> dict[str, Any]:
    with file.open("r") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise TypeError("JSON config must be an object")
    return data


def yaml_parser(file: pathlib.Path) -> dict[str, Any]:
    with file.open("r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    if not isinstance(data, dict):
        raise TypeError("YAML config must be an object")
    return data


EXTENSION_TO_PARSER_DICT: dict[str, Callable[[pathlib.Path], dict[str, Any]]] = {
    ".toml": toml_parser,
    ".json": json_parser,
    ".yaml": yaml_parser,
}
DEFAULT_PARAM_SOURCES = {ParameterSource.DEFAULT, ParameterSource.DEFAULT_MAP}
DEFAULT_CONFIG_FILES = (
    "pyproject.toml",
    "typesync.toml",
    ".typesync.toml",
    "typesync.yaml",
    ".typesync.yaml",
    "typesync.json",
    ".typesync.json",
    ".typesync",
)


def process_config(ctx: Context, config: dict[str, Any]) -> None:
    command_param_names = {param.name for param in ctx.command.params}
    for param in config:
        if param not in command_param_names:
            raise ValueError(f"invalid parameter '{param}'")

    for param in ctx.command.params:
        if param.name not in config:
            continue

        # convert a dict-like value to a tuple of (key, value)
        value = (
            list(config[param.name].items())
            if isinstance(config[param.name], dict)
            else config[param.name]
        )
        config[param.name] = param.process_value(ctx, value)


def parse_config(ctx: Context, file: str | pathlib.Path) -> dict[str, Any]:
    filepath = file if isinstance(file, pathlib.Path) else pathlib.Path(file)

    parser = EXTENSION_TO_PARSER_DICT.get(filepath.suffix)
    parsers = [parser] if parser is not None else EXTENSION_TO_PARSER_DICT.values()

    for parser in parsers:
        try:
            config = parser(filepath)
        except Exception:  # noqa: S110
            pass
        else:
            process_config(ctx, config)
            return config

    raise RuntimeError(f"invalid format '{filepath.suffix}'")


def split_parsed_from_unparsed_params(
    ctx: Context,
) -> tuple[dict[str, Any], dict[str, Any]]:
    parsed, unparsed = {}, {}
    for param, value in ctx.params.items():
        if ctx.get_parameter_source(param) in DEFAULT_PARAM_SOURCES:
            unparsed[param] = value
        else:
            parsed[param] = value
    return parsed, unparsed


def find_config_file(locations: Iterable[str]) -> pathlib.Path | None:
    for location in locations:
        path = pathlib.Path(location)
        if path.is_file():
            return path
    return None


def deep_merge(base: dict[str, Any], update_from: dict[str, Any]) -> None:
    for key, value in update_from.items():
        if key not in base or not isinstance(base[key], (dict, list, tuple)):
            base[key] = value
        elif isinstance(base[key], dict):
            deep_merge(base[key], value)
        elif isinstance(base[key], (list, tuple)):
            base[key] = (type(base[key]))({*base[key], *value})


def merge_config_params(ctx: Context, config_arg: str = "config") -> Namespace:
    params = ctx.params

    config_file_locations = (
        (params[config_arg],)
        if config_arg in params and params[config_arg] is not None
        else DEFAULT_CONFIG_FILES
    )
    config_file = find_config_file(config_file_locations)
    if config_arg in params:
        del params[config_arg]
    if config_file is None:
        raise FileNotFoundError(config_file_locations[0])

    from_config = parse_config(ctx, config_file)

    parsed_params, unparsed_params = split_parsed_from_unparsed_params(ctx)

    merged = {}
    merged.update(unparsed_params)
    merged.update(from_config)
    deep_merge(merged, parsed_params)
    return Namespace(**merged)
