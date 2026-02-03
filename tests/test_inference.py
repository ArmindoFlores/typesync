import typing
from flask import Flask

from ts_flask_urls.ts_types import TSArray, TSRecord, TSSimpleType

from conftest import ParserFixture


def test_literal_string(app: Flask, inf_return_parser: ParserFixture) -> None:
    @app.route("/main")
    def main():
        return "hello"

    assert inf_return_parser(app, "main") == TSSimpleType("string")


def test_literal_int(app: Flask, inf_return_parser: ParserFixture) -> None:
    @app.route("/main")
    def main():
        return 202

    assert inf_return_parser(app, "main") == TSSimpleType("number")


def test_literal_list_same_type(app: Flask, inf_return_parser: ParserFixture) -> None:
    @app.route("/main")
    def main():
        return [1, 2, 3]

    assert inf_return_parser(app, "main") == TSArray(TSSimpleType("number"))


def test_literal_list_mixed(app: Flask, inf_return_parser: ParserFixture) -> None:
    @app.route("/main")
    def main():
        return [1, "hello", 3]

    assert inf_return_parser(app, "main") == TSArray(TSSimpleType("any"))


def test_literal_tuple(app: Flask, inf_return_parser: ParserFixture) -> None:
    @app.route("/main")
    def main():
        return ("hello", 404)

    assert inf_return_parser(app, "main") == TSSimpleType("string")


def test_literal_dict_same_type(app: Flask, inf_return_parser: ParserFixture) -> None:
    @app.route("/main")
    def main():
        return {
            "key1": [1, 2, 3],
            "key2": [0, 1],
        }

    assert inf_return_parser(app, "main") == TSRecord(
        TSSimpleType("string"), TSArray(TSSimpleType("number"))
    )


def test_literal_dict_mixed_v(app: Flask, inf_return_parser: ParserFixture) -> None:
    @app.route("/main")
    def main():
        return {
            "key1": [1, 2, 3],
            "key2": "hello",
        }

    assert inf_return_parser(app, "main") == TSRecord(
        TSSimpleType("string"), TSSimpleType("any")
    )


def test_literal_dict_mixed_k(app: Flask, inf_return_parser: ParserFixture) -> None:
    @app.route("/main")
    def main():
        return {
            12: 1,
            "key2": 2,
        }

    assert inf_return_parser(app, "main") == TSRecord(
        TSSimpleType("any"), TSSimpleType("number")
    )


def test_literal_dict_mixed(app: Flask, inf_return_parser: ParserFixture) -> None:
    @app.route("/main")
    def main():
        return {
            12: [1, 2, 3],
            "key2": "hello",
        }

    assert inf_return_parser(app, "main") == TSSimpleType("object")


def test_function_call(app: Flask, inf_return_parser: ParserFixture) -> None:
    def result(arg: int):
        return arg

    @app.route("/main")
    def main():
        return result(12)

    assert inf_return_parser(app, "main") == TSSimpleType("number")


def test_class_factory(app: Flask, inf_return_parser: ParserFixture) -> None:
    R = typing.TypeVar("R")

    class RHProtocol(typing.Protocol[R]):
        def process(self) -> R: ...

    class TestInference:
        def process(self) -> int:
            return 12

    def make_route_function[R](
        obj: typing.Callable[[], RHProtocol[R]],
    ) -> typing.Callable[[], R]:
        def wrapper() -> R:
            inst = obj()
            return inst.process()

        return wrapper

    app.add_url_rule("/main", "main", make_route_function(TestInference))

    assert inf_return_parser(app, "main") == TSSimpleType("number")
