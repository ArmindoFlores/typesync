import typing

from typesync.ts_types import TSArray, TSObject, TSRecord, TSSimpleType, TSTuple, TSType
from typesync.utils.marshmallow_utils import MarshmallowSchemaDump
from .abstract import Translator
from .type_node import TypeNode, to_type_node


class MarshmallowTranslator(Translator):
    DEFAULT_PRIORITY = -20
    ID = "typesync.MarshmallowTranslator"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        try:
            import marshmallow  # noqa: PLC0415
        except ImportError as exc:
            raise RuntimeError(  # noqa: TRY003
                "Marshmallow support requires 'marshmallow'. "
                "Install with `pip install typesync[marshmallow]`."
            ) from exc

        self._marshmallow = marshmallow

    def _translate_marshmallow_dict(
        self, field, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ) -> TSType:
        key_type = self._get_underlying_type(field.key_field, node, generics)
        value_type = self._get_underlying_type(field.value_field, node, generics)
        return TSRecord(key_type, value_type)

    def _translate_marshmallow_list(
        self, field, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ) -> TSType:
        return TSArray(self._get_underlying_type(field.inner, node, generics))

    def _translate_marshmallow_tuple(
        self, field, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ) -> TSType:
        return TSTuple(
            [self._get_underlying_type(t, node, generics) for t in field.tuple_fields]
        )

    def _translate_marshmallow_nested(
        self, field, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ) -> TSType:
        if not isinstance(field, self._marshmallow.fields.Pluck):
            return field.nested

        if field.field_name not in field.nested.fields:
            return TSSimpleType("never")

        return self._get_underlying_type(
            field.nested.fields[field.field_name], node, generics
        )

    def _translate_marshmallow_method(
        self, field, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ) -> TSType:
        method = getattr(node.origin, field.serialize_method_name)
        return_type = to_type_node(method).hints.get("return")
        if return_type is None:
            # once Translator._type(...) is implemented, we should use that
            # instead of to_type_node to use inference if enabled
            return TSSimpleType("any")
        return self._translate(return_type, generics)

    def _translate_marshmallow_function(
        self, field, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ) -> TSType:
        return_type = to_type_node(field.serialize_func).hints.get("return")
        if return_type is None:
            # once Translator._type(...) is implemented, we should use that
            # instead of to_type_node to use inference if enabled
            return TSSimpleType("any")
        return self._translate(return_type, generics)

    def _translate_underlying_type(  # noqa: PLR0912
        self, field, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ):
        if isinstance(field, self._marshmallow.fields.Number) and field.as_string:
            return str

        match field:
            case (
                self._marshmallow.fields.IP()
                | self._marshmallow.fields.URL()
                | self._marshmallow.fields.UUID()
                | self._marshmallow.fields.Email()
                | self._marshmallow.fields.Str()
                | self._marshmallow.fields.String()
                | self._marshmallow.fields.IPv6()
                | self._marshmallow.fields.DateTime()
                | self._marshmallow.fields.IPv4()
                | self._marshmallow.fields.Url()
                | self._marshmallow.fields.Time()
                | self._marshmallow.fields.Date()
                | self._marshmallow.fields.IPv4Interface()
                | self._marshmallow.fields.IPv6Interface()
                | self._marshmallow.fields.IPInterface()
                | self._marshmallow.fields.AwareDateTime()
                | self._marshmallow.fields.NaiveDateTime()
            ):
                return str
            case self._marshmallow.fields.Bool() | self._marshmallow.fields.Boolean():
                return bool
            case self._marshmallow.fields.Constant():
                return type(field.constant)
            case (
                self._marshmallow.fields.Float() | self._marshmallow.fields.TimeDelta()
            ):
                return float
            case self._marshmallow.fields.Dict():
                return self._translate_marshmallow_dict(field, node, generics)
            case self._marshmallow.fields.Function():
                return self._translate_marshmallow_function(field, node, generics)
            case self._marshmallow.fields.Int() | self._marshmallow.fields.Integer():
                return int
            case self._marshmallow.fields.List():
                return self._translate_marshmallow_list(field, node, generics)
            case self._marshmallow.fields.Method():
                return self._translate_marshmallow_method(field, node, generics)
            case self._marshmallow.fields.Nested():
                return self._translate_marshmallow_nested(field, node, generics)
            case self._marshmallow.fields.Tuple():
                return self._translate_marshmallow_tuple(field, node, generics)
            case _:
                return TSSimpleType("never")

    def _get_underlying_type(
        self, field, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ) -> TSType:
        # FIXME: return different types depending on self.ctx.mode
        translation = self._translate_underlying_type(field, node, generics)
        if isinstance(translation, TSType):
            return translation

        return self._translate(
            to_type_node(
                translation,
                node,
            ),
            generics,
        )

    def translate(
        self, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None
    ) -> TSType | None:
        if node.origin is MarshmallowSchemaDump and len(node.args) == 1:
            return self._translate(node.args[0], generics)

        if isinstance(node.origin, self._marshmallow.Schema):
            return self._translate(to_type_node(type(node.origin), node), generics)

        if not isinstance(node.origin, type) or not issubclass(
            node.origin, self._marshmallow.Schema
        ):
            return None

        keys = tuple(node.origin._declared_fields.keys())
        value_types = tuple(
            self._get_underlying_type(value, node, generics)
            for value in node.origin._declared_fields.values()
        )

        required = tuple(
            value.required for value in node.origin._declared_fields.values()
        )
        # TODO: Handle other Marshmallow properties

        return TSObject(keys, value_types, required)
