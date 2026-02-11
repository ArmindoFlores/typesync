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
from typesync.misc import HTTPMethod
from typesync.ts_types import TSType, TSSimpleType, TSObject
from typesync.type_translators import TranslationContext, TypeNode, to_type_node

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


class RouteTypeExtractor:
    def __init__(
        self,
        app: Flask,
        rule: Rule,
        translators: tuple[type["Translator"], ...] | None = None,
        translator_priorities: dict[str, int] | None = None,
        inference_enabled: bool = False,
        inference_can_eval: bool = False,
        skip_unannotated: bool = True,
        logger: Logger | None = None,
    ) -> None:
        self.app = app
        self.rule = rule
        self.inference_enabled = inference_enabled
        self.inference_can_eval = inference_can_eval
        self.skip_unannotated = skip_unannotated
        self.logger = ClickLogger() if logger is None else logger
        self.translator_priorities = (
            {} if translator_priorities is None else translator_priorities
        )
        self.translators = self.sort_translators(
            (*self.default_translators(), *(translators or ())),
            self.translator_priorities,
        )

    @staticmethod
    def sort_translators[T: type["Translator"] | "Translator"](
        translators: typing.Iterable[T],
        priorities: dict[str, int],
    ) -> tuple[T, ...]:
        return tuple(
            sorted(translators, key=lambda t: -priorities.get(t.ID, t.DEFAULT_PRIORITY))
        )

    @staticmethod
    def default_translators() -> tuple[type["Translator"], ...]:
        from typesync.type_translators import (  # noqa: PLC0415
            AnnotationsTranslator,
            BaseTranslator,
            FlaskTranslator,
        )

        return (AnnotationsTranslator, BaseTranslator, FlaskTranslator)

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

    def parse_args_types(self) -> dict[HTTPMethod, TSType]:
        try:
            used_converters: dict[str, BaseConverter] = {
                arg: converter
                for arg, converter in (
                    (arg, self.rule._converters.get(arg, None))
                    for arg in self.rule.arguments
                )
                if converter is not None
            }

            results: dict[HTTPMethod, TSType] = {}
            for method in self.rule.methods or set():
                types: list[tuple[str, TSType]] = [
                    (arg, self._get_converter_type(arg, converter, method))
                    for arg, converter in used_converters.items()
                ]

                results[method] = (
                    TSObject([t[0] for t in types], [t[1] for t in types])
                    if len(types) > 0
                    else TSSimpleType("undefined")
                )

        except Exception as e:
            self.logger.error(f"couldn't parse argument types ({e})")
            return {}

        else:
            return results

    def translate_type(
        self, type_: Type, ctx: TranslationContext
    ) -> tuple[TSType, str | None]:
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

        translators = [Translator(translate, ctx) for Translator in self.translators]
        node = to_type_node(type_)
        return translate(node, {}), warning

    def parse_return_types(self, force_inference=False) -> dict[HTTPMethod, TSType]:
        try:
            function = self.app.view_functions[self.rule.endpoint]
            annotations = get_type_hints(function)

            ctx = TranslationContext(
                rule=self.rule,
                view_function=function,
                method="GET",
                mode="RETURN",
                inferred=False,
            )

            return_annotations = None
            if (
                not force_inference
                and annotations is not None
                and "return" in annotations
            ):
                return_annotations = annotations["return"]
            elif self.inference_enabled:
                return_annotations = infer_return_type(
                    function, self.logger, self.inference_can_eval
                )
                ctx.inferred = True

            if return_annotations is None and self.skip_unannotated:
                return {}

            route_annotations = self._get_route_annotations(return_annotations)

            results: dict[HTTPMethod, TSType] = {}
            for method in self.rule.methods or set():
                ctx.method = method
                result, warning = self.translate_type(route_annotations, ctx)

                if warning is not None and not ctx.inferred and self.inference_enabled:
                    return self.parse_return_types(force_inference=True)

                results[method] = result or TSSimpleType("any")
                if warning is not None:
                    self.logger.warning(warning)

        except Exception as e:
            self.logger.error(
                f"couldn't parse return type of '{self.rule.endpoint}' ({e})"
            )
            return {}

        else:
            return results

    def parse_json_body(self) -> dict[HTTPMethod, TSType]:
        try:
            function = self.app.view_functions[self.rule.endpoint]
            json_key = getattr(function, "_typesync_json_key", None)
            if json_key is None:
                return {}

            annotations = get_type_hints(function)
            if json_key not in annotations:
                self.logger.error(
                    f"'{self.rule.endpoint}' expected to receive JSON body as keyword "
                    f"argument '{json_key}'"
                )
                return {}

            json_body_annotations = annotations[json_key]

            ctx = TranslationContext(
                rule=self.rule,
                view_function=function,
                method="GET",
                mode="JSON",
                inferred=False,
            )
            results: dict[HTTPMethod, TSType] = {}

            for method in self.rule.methods or set():
                json_body_type, warning = self.translate_type(
                    json_body_annotations, ctx
                )
                if warning is not None:
                    self.logger.warning(warning)

                results[method] = json_body_type

        except Exception as e:
            self.logger.error(
                f"couldn't parse JSON body type of '{self.rule.endpoint}' ({e})"
            )
            return {}

        else:
            return results

    def _get_route_annotations_from_tuple(self, tp: typing.Any) -> Type:
        args = typing.get_args(tp)
        return args[0]

    def _get_route_annotations(self, tp: typing.Any) -> Type:
        origin = typing.get_origin(tp) or tp
        if origin is tuple:
            return self._get_route_annotations_from_tuple(tp)
        return tp

    def _get_converter_type(
        self, arg: str, converter: BaseConverter, method: HTTPMethod
    ) -> TSType:
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

        ctx = TranslationContext(
            rule=self.rule,
            view_function=self.app.view_functions[self.rule.endpoint],
            method=method,
            mode="ARGS",
            inferred=False,
        )

        return_annotations = annotations["return"]
        return_type, warning = self.translate_type(return_annotations, ctx)
        if warning is not None:
            self.logger.warning(warning)
        return return_type
