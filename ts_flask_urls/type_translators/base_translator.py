import types
import typing

from .abstract import Translator
from .type_node import TypeNode
from ..ts_types import TSArray, TSObject, TSType, TSRecord, TSSimpleType, TSTuple, TSUnion, is_signal


class BaseTranslator(Translator):
    def __init__(self, translate: typing.Callable[[TypeNode, dict[typing.TypeVar, TSType] | None], TSType]):
        self._translate = translate

    def _unwrap_generic(self, node: TypeNode, generics: dict[typing.TypeVar, TSType]) -> TSType:
        return generics[node.origin] if isinstance(node.origin, typing.TypeVar) else self._translate(node, generics)

    def _translate_args(self, args: tuple[TypeNode, ...], generics: dict[typing.TypeVar, TSType]) -> tuple[TSType, ...]:
        return tuple(
            self._unwrap_generic(arg, generics)
            for arg in args
        )
    
    def _translate_hints(self, hints: dict[str, TypeNode], generics: dict[typing.TypeVar, TSType]) -> dict[str, TSType]:
        return {
            key: self._unwrap_generic(hint, generics)
            for key, hint in hints.items()
        }

    def _translate_simple_type(self, origin: typing.Any) -> TSType | None:
        if origin is str:
            return TSSimpleType("string")
        elif origin is int or origin is float:
            return TSSimpleType("number")
        elif origin is bool:
            return TSSimpleType("boolean")
        elif origin is None or origin is type(None):
            return TSSimpleType("null")
        elif origin is dict:
            return TSSimpleType("object")
        elif origin is list or origin is tuple:
            return TSArray(TSSimpleType("any"))
        elif origin is typing.Any:
            return TSSimpleType("any")
        elif origin is typing.Never:
            return TSSimpleType("never")
        elif origin is ...:
            # Special signal value
            return TSSimpleType("...")
        return None

    def _translate_complex_type(self, node: TypeNode, generics: dict[typing.TypeVar, TSType]) -> TSType | None:
        translated_args = self._translate_args(node.args, generics)

        if node.origin is dict:
            if len(translated_args) != 2:
                return None
            return TSRecord(*translated_args)

        if node.origin is list:
            if len(translated_args) != 1:
                return None
            return TSArray(translated_args[0])
        
        if node.origin is tuple:
            if len(translated_args) == 0:
                return TSArray(TSSimpleType("any"))
            if is_signal(translated_args[-1]) and len(translated_args) == 2:
                return TSArray(translated_args[0])
            return TSTuple(translated_args)
        
        if node.origin is types.UnionType or node.origin is typing.Union:
            return TSUnion(translated_args)
        
    def _translate_typed_dict(self, node: TypeNode, generics: dict[typing.TypeVar, TSType]) -> TSType | None:
        translated_args = self._translate_args(node.args, generics)
        translated_hints = self._translate_hints(node.hints, dict(zip(node.params, translated_args)))

        keys = tuple(node.hints.keys())
        required = tuple(
            node.origin is not typing.NotRequired 
            for node in node.hints.values()
        )
        value_types = tuple(
            arg_value 
            for arg_value in translated_hints.values()
        )
        return TSObject(keys, value_types, required)

    def _translate_type_alias(self, node: TypeNode, generics: dict[typing.TypeVar, TSType]) -> TSType | None:
        if node.value is None:
            return None
        translated_args = self._translate_args(node.args, generics)
        return self._translate(node.value, dict(zip(node.params, translated_args)))

    def translate(self, node: TypeNode, generics: dict[typing.TypeVar, TSType] | None) -> TSType | None:
        generics = generics or {}
        
        if isinstance(node.origin, typing.TypeAliasType):
            return self._translate_type_alias(node, generics)
        
        if typing.is_typeddict(node.origin):
            return self._translate_typed_dict(node, generics)

        if len(node.args) == 0:
            return self._translate_simple_type(node.origin)

        return self._translate_complex_type(node, generics)
