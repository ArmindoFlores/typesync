import typing

import click
from flask import Flask
from werkzeug.routing import (
    FloatConverter,
    BaseConverter,
    IntegerConverter,
    UUIDConverter,
    PathConverter,
    UnicodeConverter,
)
from werkzeug.routing.rules import Rule

from .inference import infer_return_type
from typesync.ts_types import TSType, TSSimpleType, TSObject
from typesync.type_translators import TypeNode, to_type_node

if typing.TYPE_CHECKING:
    from typesync.type_translators import Translator


type Type = typing.Any
type TypeTreeTuple = tuple[TypeTree, ...]
type TypeTreeDict = dict[str, TypeTree]
type TypeTree = Type | tuple[Type, TypeTreeTuple | TypeTreeDict]
type GenericParamValues = dict[typing.TypeVar, TypeTree]


class Logger(typing.Protocol):
    def info(self, text: str) -> None: ...
    def warning(self, text: str) -> None: ...
    def error(self, text: str) -> None: ...


class ClickLogger:
    @staticmethod
    def info(text: str) -> None:
        click.echo(f"Info: {text}")

    @staticmethod
    def warning(text: str) -> None:
        click.secho(f"Warning: {text}", fg="yellow")

    @staticmethod
    def error(text: str) -> None:
        click.secho(f"Error: {text}", fg="red")


def get_type_hints(tp: typing.Any) -> dict[str, typing.Any]:
    return getattr(tp, "__annotations__", {})


class FlaskRouteTypeExtractor:
    def __init__(
        self,
        app: Flask,
        rule: Rule,
        translators: tuple[type["Translator"]] | None = None,
        translator_priorities: dict[str, int] | None = None,
        inference_enabled: bool = False,
        inference_can_eval: bool = False,
        logger: Logger | None = None,
    ) -> None:
        self.app = app
        self.rule = rule
        self.inference_enabled = inference_enabled
        self.inference_can_eval = inference_can_eval
        self.logger = ClickLogger() if logger is None else logger
        self.translator_priorities = (
            {} if translator_priorities is None else translator_priorities
        )
        self.translators = self._sort_translators(
            (*self.default_translators(), *(translators or ())),
            self.translator_priorities,
        )

    @staticmethod
    def _sort_translators(
        translators: typing.Iterable["Translator"],
        priorities: dict[str, int] | None = None,
    ) -> tuple["Translator"]:
        return tuple(
            sorted(translators, key=lambda t: -priorities.get(t.ID, t.DEFAULT_PRIORITY))
        )

    @staticmethod
    def default_translators() -> tuple[type["Translator"], ...]:
        from typesync.type_translators import BaseTranslator, FlaskTranslator  # noqa: PLC0415

        return (BaseTranslator, FlaskTranslator)

    @property
    def rule_name(self) -> str:
        return self.rule.endpoint.replace(".", "_")

    @property
    def rule_url(self) -> str:
        return "".join(
            [(f"<{content}>" if arg else content) for arg, content in self.rule._trace][
                1:
            ]
        )

    def parse_args_type(self) -> TSType | None:
        try:
            used_converters: dict[str, BaseConverter] = {
                arg: converter
                for arg, converter in (
                    (arg, self.rule._converters.get(arg, None))
                    for arg in self.rule.arguments
                )
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

    def translate_type(self, type_: Type) -> tuple[TSType, str | None]:
        warning = None

        def translate(
            node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
        ) -> TSType:
            nonlocal warning
            for translator in translators:
                r = translator.translate(node, generics)
                if r is not None:
                    return r

            warning = (
                f"can't translate '{getattr(node.origin, '__name__', node.origin)}'"
                " to a TypeScript equivalent, defaulting to 'any'"
            )
            return TSSimpleType("any")

        translators = [Translator(translate) for Translator in self.translators]
        node = to_type_node(type_)
        return translate(node, {}), warning

    def parse_return_type(self) -> TSType | None:
        try:
            function = self.app.view_functions[self.rule.endpoint]
            annotations = get_type_hints(function)
            if annotations is not None and "return" in annotations:
                return_annotations = annotations["return"]
                route_return_annotations = self._get_route_annotations(
                    return_annotations
                )
                return_type, warning = self.translate_type(route_return_annotations)
            else:
                return_type = warning = None

            if self.inference_enabled and (return_type is None or warning is not None):
                route_return_type = infer_return_type(
                    function, self.logger, self.inference_can_eval
                )
                if route_return_type is not None:
                    return_type, warning = self.translate_type(
                        self._get_route_annotations(route_return_type)
                    )

            if warning is not None:
                self.logger.warning(warning)

            return return_type or TSSimpleType("any")

        except Exception as e:
            self.logger.error(
                f"couldn't parse return type of '{self.rule.endpoint}' ({e})"
            )
            return None

        else:
            return TSSimpleType("any") if return_type is None else return_type

    def parse_json_body(self) -> TSType | None:
        try:
            function = self.app.view_functions[self.rule.endpoint]
            json_key = getattr(function, "_typesync", None)
            if json_key is None:
                return None

            annotations = get_type_hints(function)
            if json_key not in annotations:
                self.logger.error(
                    f"'{self.rule.endpoint}' expected to receive JSON body as keyword "
                    f"argument '{json_key}'"
                )
                return None

            json_body_annotations = annotations[json_key]
            json_body_type, warning = self.translate_type(json_body_annotations)
            if warning is not None:
                self.logger.warning(warning)

        except Exception as e:
            self.logger.error(
                f"couldn't parse JSON body type of '{self.rule.endpoint}' ({e})"
            )
            return None

        else:
            return json_body_type

    def _get_route_annotations_from_tuple(self, tp: typing.Any) -> Type:
        args = typing.get_args(tp)
        return args[0]

    def _get_route_annotations(self, tp: typing.Any) -> Type:
        origin = typing.get_origin(tp) or tp
        if origin is tuple:
            return self._get_route_annotations_from_tuple(tp)
        return tp

    def _get_converter_type(self, arg: str, converter: BaseConverter) -> TSType:
        if isinstance(converter, (FloatConverter, IntegerConverter)):
            return TSSimpleType("number")
        if isinstance(converter, (UUIDConverter, PathConverter, UnicodeConverter)):
            return TSSimpleType("string")

        # Custom converter, check to_python() annotations
        annotations = get_type_hints(converter.to_python)
        if annotations is None or "return" not in annotations:
            self.logger.warning(
                f"route '{self.rule.endpoint}', argument '{arg}': using non-standard"
                "converter without type annotations, defaulting to 'string'",
            )
            return TSSimpleType("string")

        return_annotations = annotations["return"]
        return_type, warning = self.translate_type(return_annotations)
        if warning is not None:
            self.logger.warning(warning)
        return return_type
