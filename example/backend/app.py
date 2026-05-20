import datetime
import sys

from marshmallow import Schema, fields
import pydantic

from typesync.utils.marshmallow_utils import (
    MarshmallowSchemaDump,
    marshmallow_schema_dump,
)

sys.path.append("../..")

import typing

import flask
from flask_cors import CORS
from werkzeug.routing import BaseConverter

import typesync
from typesync.utils import Response, Loadable, jsonify, with_json_body, deferred


class CustomConverter(BaseConverter):
    regex = r"(true)|(false)"

    def to_python(self, value: str) -> bool:
        return value == "true"

    def to_url(self, value: bool) -> str:
        return "true" if value else "false"


class APIResult[T, Y](typing.TypedDict):
    result: tuple[T, Y]
    x: typing.NotRequired[int]
    y: typing.NotRequired[bool]


type InnerAlias[A, B, C] = tuple[A, B, C]
type Sandwich[T, K] = InnerAlias[T, K, T]
type IntOrString = int | str

type Alias1[A] = list[A]
type Alias2[B] = Alias1[B]
type AliasedArgs[A, B] = dict[str, tuple[Alias1[B], Alias2[A]]]

app = flask.Flask(__name__)
CORS(app, origins=["http://localhost:*", "http://127.0.0.1:*"])
app.cli.add_command(typesync.cli)
app.url_map.converters["boolean"] = CustomConverter


@app.route("/main", methods=("GET", "POST"))
def main() -> APIResult[IntOrString, bool | None]:
    return {
        "result": (1, True),
    }


@app.route("/complex")
def complex_() -> dict[str, tuple[IntOrString, ...]]:
    return {
        "entry1": (1, "a", 2),
        "entry2": ("x", "y"),
    }


@app.route("/with/<boolean:arg>/args")
def with_args(arg: bool) -> Response[tuple[Sandwich[bool, str], int]]:
    value: Sandwich[bool, str] = (arg, str(arg), arg)
    return jsonify((value, 200))


class MyModel(pydantic.BaseModel):
    x: int


@app.route("/pydantic", methods=("POST",))
@with_json_body(loader=deferred(MyModel.model_validate))
def pydantic(json: Loadable[MyModel]) -> Response[AliasedArgs[int, bool]]:
    model = json.load()
    return jsonify({"hello": ([], [model.x])})


def _first_name(obj) -> str:
    return obj["name"].split(" ")[0]


class ArtistSchema(Schema):
    name = fields.Str(required=True)
    first_name = fields.Function(_first_name)
    age = fields.Method("_age")
    date_birth = fields.Date()
    is_famous = fields.Bool()

    def _age(self, schema: object) -> int | None:
        if "date_birth" not in schema:
            return None
        return (datetime.date.today() - schema["date_birth"]).days // 365


@app.route("/mm")
def mm() -> MarshmallowSchemaDump[ArtistSchema]:
    return marshmallow_schema_dump(
        ArtistSchema(),
        {
            "name": "John Doe",
            "date_birth": datetime.date(2001, 5, 4),
            "is_famous": False,
        },
    )
