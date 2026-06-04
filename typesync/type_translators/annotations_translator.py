import typing


from .abstract import Translator
from .type_node import TypeNode
from typesync import annotations
from typesync.ts_types import TSSimpleType, TSType


class AnnotationsTranslator(Translator):
    DEFAULT_PRIORITY = -100
    ID = "typesync.AnnotationsTranslator"

    def _translate_http_method_annotation(
        self,
        node: TypeNode,
        annotation: annotations.TypesyncHTTPMethodAnnotation,
        generics: dict[typing.TypeVar, TSType] | None,
    ) -> TSType | None:
        if self.ctx.method in annotation.methods:
            return self._translate(node, generics)
        return TSSimpleType("never")

    def _translate_annotation(
        self,
        node: TypeNode,
        annotation: typing.Any,
        generics: dict[typing.TypeVar, TSType] | None,
    ) -> TSType | None:
        match annotation:
            case annotations.TypesyncHTTPMethodAnnotation():
                return self._translate_http_method_annotation(
                    node, annotation, generics
                )
            case annotations.TypesyncSkipGenerationAnnotation():
                self._skip_route()
                return TSSimpleType("never")

        return self._translate(node, generics)

    def translate(
        self, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ) -> TSType | None:
        if node.origin is not typing.Annotated:
            return None

        if len(node.args) != 1:
            return None

        return self._translate_annotation(node.args[0], node.annotation, generics)
