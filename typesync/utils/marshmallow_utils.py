import marshmallow
import typing


class MarshmallowSchemaDump[T: marshmallow.Schema]:
    """Wrapper around a Marshmallow schema's JSON output."""


def marshmallow_schema_dump[T: marshmallow.Schema](
    schema: T, obj: typing.Any
) -> MarshmallowSchemaDump[T]:
    return typing.cast(MarshmallowSchemaDump[T], schema.dump(obj))
