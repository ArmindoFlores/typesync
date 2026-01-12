from flask import Flask

from ts_flask_urls.ts_types import TSSimpleType, TSTuple
from ts_flask_urls.stubs import Response, jsonify

from conftest import ParserFixture


def test_jsonify_none(app: Flask, return_parser: ParserFixture) -> None:
    @app.route("/main")
    def main() -> Response[None]:
        return jsonify(None)
    
    assert return_parser(app, "main") == TSSimpleType("null")

def test_jsonify_tuple(app: Flask, return_parser: ParserFixture) -> None:
    @app.route("/main")
    def main() -> Response[tuple[int, str, int]]:
        return jsonify((1, "hello", 4))
    
    assert return_parser(app, "main") == TSTuple((
        TSSimpleType("number"),
        TSSimpleType("string"),
        TSSimpleType("number"),
    ))
