import typing

import flask
import pytest

from typesync.ts_types import TSType
from typesync.codegen.extractor import RouteTypeExtractor


@pytest.fixture
def app():
    app = flask.Flask(__name__)
    return app


type ParserFixture = typing.Callable[[flask.Flask, str], TSType | None]


@pytest.fixture
def args_parser():
    def inner(app: flask.Flask, endpoint: str) -> TSType | None:
        rules = app.url_map.iter_rules()
        for rule in rules:
            if rule.endpoint == endpoint:
                return (
                    RouteTypeExtractor(
                        app, rule, translators=RouteTypeExtractor.all_translators()
                    )
                    .parse_args_types()
                    .get("GET")
                )
        return None

    return inner


@pytest.fixture
def return_parser():
    def inner(app: flask.Flask, endpoint: str) -> TSType | None:
        rules = app.url_map.iter_rules()
        for rule in rules:
            if rule.endpoint == endpoint:
                return (
                    RouteTypeExtractor(
                        app, rule, translators=RouteTypeExtractor.all_translators()
                    )
                    .parse_return_types()
                    .get("GET")
                )
        return None

    return inner


@pytest.fixture
def json_body_parser():
    def inner(app: flask.Flask, endpoint: str) -> TSType | None:
        rules = app.url_map.iter_rules()
        for rule in rules:
            if rule.endpoint == endpoint:
                return (
                    RouteTypeExtractor(
                        app, rule, translators=RouteTypeExtractor.all_translators()
                    )
                    .parse_json_body()
                    .get("POST")
                )
        return None

    return inner


@pytest.fixture
def inf_return_parser():
    def inner(app: flask.Flask, endpoint: str) -> TSType | None:
        rules = app.url_map.iter_rules()
        for rule in rules:
            if rule.endpoint == endpoint:
                return (
                    RouteTypeExtractor(
                        app,
                        rule,
                        inference_enabled=True,
                        inference_can_eval=True,
                        translators=RouteTypeExtractor.all_translators(),
                    )
                    .parse_return_types()
                    .get("GET")
                )
        return None

    return inner
