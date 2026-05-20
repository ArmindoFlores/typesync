import abc
import typing


if typing.TYPE_CHECKING:
    from . import TypeNode
    from .context import TranslationContext
    from typesync.ts_types import TSType


class Translator(abc.ABC):
    DEFAULT_PRIORITY: int = 0
    ID: str

    def __init__(
        self,
        translate: typing.Callable[
            ["TypeNode", dict[typing.TypeVar, "TSType"] | None], "TSType"
        ],
        get_type: typing.Callable[[typing.Callable], "TypeNode | None"],
        ctx: "TranslationContext",
    ) -> None:
        self._translate = translate
        self._get_type = get_type
        self.ctx = ctx

    @abc.abstractmethod
    def translate(
        self, node: "TypeNode", generics: dict[typing.TypeVar, "TSType"] | None
    ) -> "TSType | None": ...
