import dataclasses
import typing

from flask.typing import RouteCallable
from werkzeug.routing.rules import Rule

from typesync.misc import HTTPMethod


@dataclasses.dataclass
class TranslationContext:
    rule: Rule
    view_function: RouteCallable
    method: HTTPMethod
    mode: typing.Literal["JSON", "RETURN", "ARGS"]
    inferred: bool
