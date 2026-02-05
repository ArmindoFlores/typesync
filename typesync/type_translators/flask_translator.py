import typing

from .abstract import Translator
from .type_node import TypeNode
from typesync.ts_types import TSType
from typesync.utils import Response


class FlaskTranslator(Translator):
    DEFAULT_PRIORITY = -10
    ID = "typesync.FlaskTranslator"

    def translate(
        self, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ) -> TSType | None:
        if node.origin is Response:
            if len(node.args) != 1:
                return None
            return self._translate(node.args[0], generics)
        return None
