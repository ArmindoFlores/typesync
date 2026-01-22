import abc
import typing

if typing.TYPE_CHECKING:
    from . import TypeNode
    from ..ts_types import TSType


class Translator(abc.ABC):
    @abc.abstractmethod
    def __init__(self, convert: typing.Callable[["TypeNode", dict[typing.TypeVar, "TSType"] | None], "TSType"]) -> None:
        ...

    @abc.abstractmethod
    def translate(self, node: "TypeNode", generics: dict[typing.TypeVar, "TSType"] | None) -> "TSType | None":
        ...
