import sys
sys.path.append("../..")

import typing

import flask
from flask_cors import CORS
from werkzeug.routing import BaseConverter

import ts_flask_urls
from ts_flask_urls.stubs import Response, jsonify


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
app.cli.add_command(ts_flask_urls.cli)
app.url_map.converters["boolean"] = CustomConverter


@app.route("/main")
def main() -> APIResult[IntOrString, typing.Optional[bool]]:
    return {
        "result": (1, True)
    }

@app.route("/complex")
def complex() -> dict[str, tuple[IntOrString, ...]]:
    return {
        "entry1": (1, "a", 2),
        "entry2": ("x", "y"),
    }

@app.route("/with/<boolean:arg>/args")
def with_args(arg: bool) -> Response[tuple[Sandwich[bool, str], int]]:
    value: Sandwich[bool, str] = (arg, str(arg), arg)
    return jsonify((value, 200))

@app.route("/pytest")
def pytest() -> Response[AliasedArgs[int, bool]]:
    return jsonify({})
