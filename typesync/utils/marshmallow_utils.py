import marshmallow
import typing


# IMPORTANT: MarshmallowSchemaDump should not be instantiated! It is not
# actually guaranteed to be a dict
class MarshmallowSchemaDump[T: marshmallow.Schema](dict):
    """Wrapper around a Marshmallow schema's JSON output."""

    def __init__(self, *args, **kwargs):
        raise RuntimeError("This class should never be instantiated")  # noqa: TRY003


class Schema(marshmallow.Schema):
    # FIXME: implement other useful methods
    def dump(
        self, obj: typing.Any, *, many: bool | None = None
    ) -> MarshmallowSchemaDump[typing.Self]:
        return super().dump(obj, many=many)


def marshmallow_schema_dump[T: marshmallow.Schema](
    schema: T, obj: typing.Any
) -> MarshmallowSchemaDump[T]:
    return typing.cast(MarshmallowSchemaDump[T], schema.dump(obj))
