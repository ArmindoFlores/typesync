import marshmallow
import typing

from typesync.annotations import TypesyncAnnotation


class TypesyncMarshmallowAnnotation(TypesyncAnnotation):
    def __init__(self, schema: marshmallow.Schema) -> None:
        self.schema = schema


# IMPORTANT: MarshmallowSchemaDump should not be instantiated! It is not
# actually guaranteed to be a dict
class MarshmallowSchemaDump[T: marshmallow.Schema](dict):
    """Wrapper around a Marshmallow schema's JSON output."""

    def __init__(self, *args, **kwargs):
        raise RuntimeError("This class should never be instantiated")


class LoadedMarshmallowSchema[T: marshmallow.Schema](dict[str, typing.Any]):
    """Wrapper around a dict constructed from a Marshmallow schema's `.load` method."""

    def __init__(self, *args, **kwargs):
        raise RuntimeError("This class should never be instantiated")


class Schema(marshmallow.Schema):
    # FIXME: implement other useful methods
    def dump(
        self, obj: typing.Any, *, many: bool | None = None
    ) -> MarshmallowSchemaDump[typing.Self]:
        return super().dump(obj, many=many)


def marshmallow_schema_dump[T: marshmallow.Schema](
    schema: T, obj: typing.Any
) -> MarshmallowSchemaDump[T]:
    if schema.many:
        raise RuntimeError(
            f"schema {schema} has many=True, "
            "use marshmallow_schema_dump_many(...) instead"
        )
    return typing.cast(MarshmallowSchemaDump[T], schema.dump(obj))


def marshmallow_schema_dump_many[T: marshmallow.Schema](
    schema: T, obj: typing.Any
) -> list[MarshmallowSchemaDump[T]]:
    if not schema.many:
        raise RuntimeError(
            f"schema {schema} has many=False, use marshmallow_schema_dump(...) instead"
        )
    return typing.cast(list[MarshmallowSchemaDump[T]], schema.dump(obj))
