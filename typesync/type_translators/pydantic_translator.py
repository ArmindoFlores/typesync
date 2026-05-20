import typing

from typesync.ts_types import TSObject, TSType
from typesync.utils.pydantic_utils import PydanticModelDump
from .abstract import Translator
from .type_node import TypeNode, to_type_node


class PydanticTranslator(Translator):
    DEFAULT_PRIORITY = -20
    ID = "typesync.PydanticTranslator"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        try:
            import pydantic  # noqa: PLC0415
        except ImportError as exc:
            raise RuntimeError(  # noqa: TRY003
                "Pydantic support requires 'pydantic'. "
                "Install with `pip install typesync[pydantic]`."
            ) from exc

        self._pydantic = pydantic

    def translate(
        self, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ) -> TSType | None:
        if node.origin is PydanticModelDump and len(node.args) == 1:
            return self._translate(node.args[0], generics)

        if not isinstance(node.origin, type) or not issubclass(
            node.origin, self._pydantic.BaseModel
        ):
            return None

        keys = tuple(node.origin.model_fields.keys())
        value_types = tuple(
            self._translate(to_type_node(value.annotation, node), generics)
            for value in node.origin.model_fields.values()
        )
        required = tuple(
            value.is_required() for value in node.origin.model_fields.values()
        )
        # TODO: Handle other Pydantic properties
        # TODO: Handle Pydantic computed properties

        return TSObject(keys, value_types, required)
