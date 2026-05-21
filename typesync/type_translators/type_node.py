import dataclasses
import typing


class RecursiveCallClass:
    def __repr__(self):
        return "RecursiveCall"


RecursiveCall = RecursiveCallClass()


@dataclasses.dataclass(frozen=True)
class TypeNode:
    origin: typing.Any
    params: tuple[typing.TypeVar, ...]
    args: tuple["TypeNode", ...]
    hints: dict[str, "TypeNode"]
    value: "TypeNode | None"
    annotation: typing.Any

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
        if self.annotation is not None:
            s += f" annotation={self.annotation}"
        return s + ">"


def to_type_node(
    type_: typing.Any, original_type: TypeNode | None = None, mapping=None
) -> TypeNode:
    mapping = {} if mapping is None else mapping
    origin = typing.get_origin(type_) or type_
    params: tuple[typing.TypeVar, ...] = getattr(origin, "__type_params__", ())
    args: tuple[TypeNode, ...] = ()
    annotations = []
    if origin is not typing.Annotated:
        args = tuple(
            to_type_node(arg, original_type, mapping) for arg in typing.get_args(type_)
        )
    else:
        base_args = typing.get_args(type_)
        if len(base_args) > 0:
            args = (to_type_node(base_args[0], original_type, mapping),)
            annotations = list(base_args[1:])
    hints = {
        key: to_type_node(hint, original_type, mapping)
        for key, hint in getattr(origin, "__annotations__", {}).items()
    }
    patched_args = args
    if original_type is not None and origin is original_type.origin:
        mapping = {
            param: mapping.get(arg.origin, arg)
            for param, arg in zip(original_type.params, args, strict=True)
        }
        patched_args = tuple(mapping[param] for param in params)
        if all(
            (
                arg.origin == original_param
                for arg, original_param in zip(
                    patched_args, original_type.params, strict=True
                )
            )
        ):
            origin = RecursiveCall

    node = TypeNode(
        origin=origin,
        params=params,
        args=args,
        hints=hints,
        annotation=annotations[0] if len(annotations) > 0 else None,
        value=(
            to_type_node(
                origin.__value__,
                TypeNode(
                    origin=origin,
                    params=params,
                    args=patched_args,
                    hints=hints,
                    value=None,
                    annotation=(),
                ),
                mapping=mapping,
            )
            if hasattr(origin, "__value__")
            else None
        ),
    )
    for annotation in annotations[1:]:
        new_node = TypeNode(
            origin=typing.Annotated,
            params=params,
            args=(node,),
            hints={},
            annotation=annotation,
            value=None,
        )
        node = new_node
    return node
