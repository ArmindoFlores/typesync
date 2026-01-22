import typing

from .abstract import Translator
from .type_node import TypeNode
from ..ts_types import TSType
from ..stubs import Response


class FlaskTranslator(Translator):
    def __init__(self, translate: typing.Callable[[TypeNode, dict[typing.TypeVar, TSType] | None], TSType]) -> None:
        self._translate = translate

    def translate(self, node: TypeNode, generics: dict[typing.TypeVar, TSType]) -> TSType | None:
        if node.origin is Response:
            if len(node.args) != 1:
                return None
            return self._translate(node.args[0], generics)
        return None
