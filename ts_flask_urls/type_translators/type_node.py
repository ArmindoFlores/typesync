import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class TypeNode:
    origin: typing.Any
    params: tuple[typing.TypeVar]
    args: tuple["TypeNode", ...]
    hints: dict[str, "TypeNode"]
    value: "TypeNode | None"
    
    def __repr__(self) -> str:
        s = f"<TypeNode {getattr(self.origin, '__name__', self.origin)}"
        if len(self.params):
            s += f" params={self.params}"
        if len(self.args):
            s += f" args={self.args}"
        if len(self.hints):
            s += f" hints={self.hints}"
        if self.value is not None:
            s += f" value={self.value}"
        return s + ">"


def to_type_node(type_: typing.Any) -> TypeNode:
    origin = typing.get_origin(type_) or type_
    return TypeNode(
        origin=origin,
        params=getattr(origin, "__type_params__", tuple()),
        args=tuple(to_type_node(arg) for arg in typing.get_args(type_)),
        hints={key: to_type_node(hint) for key, hint in getattr(origin, "__annotations__", {}).items()},
        value=to_type_node(origin.__value__) if hasattr(origin, "__value__") else None
    )
