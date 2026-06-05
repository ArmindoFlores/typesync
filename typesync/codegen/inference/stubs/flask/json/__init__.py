__all__ = [
    "jsonify",
]

import ast
import typing

from typesync.codegen.inference import Infer
from typesync.utils.base_utils import Array


def jsonify(infer: typing.Callable[[], None], args: list[ast.expr], kwargs: dict[str, ast.expr]) -> Infer:
    # 1. If there is only one arg, jsonify's return type is inferred from it
    if len(args) == 1:
        t = infer(args[0])
        if typing.get_origin(t) is tuple:
            t = Array[*typing.get_args(t)]
        return t
    # 2. If there are multiple args, the return type is a tuple
    if len(args) > 1:
        result = Array[*(infer(arg) for arg in args)]
        return result
    # 3. If keyword arguments were specified, the return type is a dict with the
    # same shape as kwargs
    if len(kwargs):
        return dict
    return typing.Any
