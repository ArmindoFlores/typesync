import pydantic
import typing


class PydanticModelDump[T: pydantic.BaseModel]:
    """Wrapper around a Pydantic model's JSON output."""


def pydantic_model_dump[T: pydantic.BaseModel](model: T) -> PydanticModelDump[T]:
    return typing.cast(PydanticModelDump[T], model.model_dump())
