import sys

sys.path.append("../..")

import typing

import flask
from flask_cors import CORS
from werkzeug.routing import BaseConverter

import ts_flask_urls
from ts_flask_urls.utils import Response, jsonify


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


@app.route("/main", methods=("GET", "POST"))
def main() -> APIResult[IntOrString, bool | None]:
    return {
        "result": (1, True),
    }


@app.route("/complex")
def complex_() -> dict[str, tuple[IntOrString, ...]]:
    return {
        "entry1": (1, "a", 2),
        "entray2": ("x", "y"),
    }


@app.route("/with/<boolean:arg>/args")
def with_args(arg: bool) -> Response[tuple[Sandwich[bool, str], int]]:
    value: Sandwich[bool, str] = (arg, str(arg), arg)
    return jsonify((value, 200))


@app.route("/pytest")
@ts_flask_urls.utils.json_kwarg
def pytest(json: int) -> Response[AliasedArgs[int, bool]]:
    return jsonify({"hello": ([], [json])})


class TestInference:
    def _inferred(self) -> dict[str, int]:
        return {"hello": 13}


@app.route("/inferred")
def inferred():
    hello = "str"
    return (1, hello, 2)
