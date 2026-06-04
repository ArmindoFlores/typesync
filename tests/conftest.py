import typing

import flask
import pytest

from typesync.ts_types import TSType
from typesync.codegen.extractor import Logger, RouteTypeExtractor


@pytest.fixture
def app():
    app = flask.Flask(__name__)
    return app


type ParserFixture = typing.Callable[[flask.Flask, str, Logger | None], TSType | None]


class PytestLogger(Logger):
    def __init__(self) -> None:
        self.error_calls: list[str] = []
        self.warning_calls: list[str] = []
        self.info_calls: list[str] = []

    def info(self, text: str) -> None:
        self.info_calls.append(text)

    def warning(self, text: str) -> None:
        self.warning_calls.append(text)

    def error(self, text: str) -> None:
        self.error_calls.append(text)


@pytest.fixture
def logger():
    return PytestLogger()


@pytest.fixture
def args_parser():
    def inner(
        app: flask.Flask, endpoint: str, logger: Logger | None = None
    ) -> TSType | None:
        rules = app.url_map.iter_rules()
        for rule in rules:
            if rule.endpoint == endpoint:
                return (
                    RouteTypeExtractor(
                        app,
                        rule,
                        translators=RouteTypeExtractor.all_translators(),
                        logger=logger,
                        methods={"GET"},
                    )
                    .parse_args_types()
                    .get("GET")
                )
        return None

    return inner


@pytest.fixture
def return_parser():
    def inner(
        app: flask.Flask, endpoint: str, logger: Logger | None = None
    ) -> TSType | None:
        rules = app.url_map.iter_rules()
        for rule in rules:
            if rule.endpoint == endpoint:
                return (
                    RouteTypeExtractor(
                        app,
                        rule,
                        translators=RouteTypeExtractor.all_translators(),
                        logger=logger,
                        methods={"GET"},
                    )
                    .parse_return_types()
                    .get("GET")
                )
        return None

    return inner


@pytest.fixture
def json_body_parser():
    def inner(
        app: flask.Flask, endpoint: str, logger: Logger | None = None
    ) -> TSType | None:
        rules = app.url_map.iter_rules()
        for rule in rules:
            if rule.endpoint == endpoint:
                return (
                    RouteTypeExtractor(
                        app,
                        rule,
                        translators=RouteTypeExtractor.all_translators(),
                        logger=logger,
                        methods={"POST"},
                    )
                    .parse_json_body()
                    .get("POST")
                )
        return None

    return inner


@pytest.fixture
def inf_return_parser():
    def inner(
        app: flask.Flask, endpoint: str, logger: Logger | None = None
    ) -> TSType | None:
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
                        logger=logger,
                        methods={"GET"},
                    )
                    .parse_return_types()
                    .get("GET")
                )
        return None

    return inner
