import datetime

from flask import Flask
from marshmallow import Schema, fields

from typesync.ts_types import TSArray, TSObject, TSSimpleType, TSUnion
from typesync.utils.marshmallow_utils import (
    MarshmallowSchemaDump,
    marshmallow_schema_dump,
)

from conftest import ParserFixture


def test_simple_model(app: Flask, return_parser: ParserFixture) -> None:
    class ArtistSchema(Schema):
        name = fields.Str(required=True)
        age = fields.Integer()
        date_birth = fields.Date()
        is_famous = fields.Bool()

    @app.route("/main")
    def main() -> MarshmallowSchemaDump[ArtistSchema]:
        return marshmallow_schema_dump(
            ArtistSchema(),
            {
                "name": "John Doe",
                "age": 25,
                "date_birth": datetime.date(2001, 1, 1),
                "is_famous": False,
            },
        )

    assert return_parser(app, "main") == TSObject(
        keys=("name", "age", "date_birth", "is_famous"),
        value_types=(
            TSSimpleType("string"),
            TSSimpleType("number"),
            TSSimpleType("string"),
            TSSimpleType("boolean"),
        ),
        required=(True, False, False, False),
    )


def test_complex_model(app: Flask, return_parser: ParserFixture) -> None:
    class ArtistSchema(Schema):
        name = fields.Str(required=True)
        age = fields.Integer()
        date_birth = fields.Date()
        is_famous = fields.Bool()

    class Song(Schema):
        name = fields.Str(required=True)
        duration = fields.Integer(as_string=True, required=True)

    class AlbumSchema(Schema):
        title = fields.Str(required=True)
        release_date = fields.Date()
        songs = fields.List(fields.Nested(Song()), required=True)
        artist = fields.Nested(ArtistSchema(), required=True)

    @app.route("/main")
    def main() -> MarshmallowSchemaDump[AlbumSchema]:
        return marshmallow_schema_dump(
            AlbumSchema(),
            {
                "title": "Hello World!",
                "release_date": datetime.date(2024, 5, 6),
                "songs": [],
                "artist": {
                    "name": "John Doe",
                    "age": 25,
                    "date_birth": datetime.date(2001, 1, 1),
                    "is_famous": False,
                },
            },
        )

    assert return_parser(app, "main") == TSObject(
        keys=("title", "release_date", "songs", "artist"),
        value_types=(
            TSSimpleType("string"),
            TSSimpleType("string"),
            TSArray(
                TSObject(
                    keys=("name", "duration"),
                    value_types=(TSSimpleType("string"), TSSimpleType("string")),
                    required=(True, True),
                )
            ),
            TSObject(
                keys=("name", "age", "date_birth", "is_famous"),
                value_types=(
                    TSSimpleType("string"),
                    TSSimpleType("number"),
                    TSSimpleType("string"),
                    TSSimpleType("boolean"),
                ),
                required=(True, False, False, False),
            ),
        ),
        required=(True, False, True, True),
    )


def test_method_and_function(app: Flask, return_parser: ParserFixture) -> None:
    def _first_name(schema: dict) -> str:
        return schema["name"].split(" ")[0]

    class ArtistSchema(Schema):
        name = fields.Str(required=True)
        first_name = fields.Function(_first_name)
        age = fields.Method("_age")
        date_birth = fields.Date()
        is_famous = fields.Bool()

        def _age(self, schema: dict) -> int | None:
            if "date_birth" not in schema:
                return None
            return (datetime.date.today() - schema["date_birth"]).days // 365

    @app.route("/main")
    def main() -> MarshmallowSchemaDump[ArtistSchema]:
        return marshmallow_schema_dump(
            ArtistSchema(),
            {
                "name": "John Doe",
                "date_birth": datetime.date(2001, 1, 1),
                "is_famous": False,
            },
        )

    assert return_parser(app, "main") == TSObject(
        keys=("name", "first_name", "age", "date_birth", "is_famous"),
        value_types=(
            TSSimpleType("string"),
            TSSimpleType("string"),
            TSUnion((TSSimpleType("number"), TSSimpleType("null"))),
            TSSimpleType("string"),
            TSSimpleType("boolean"),
        ),
        required=(True, False, False, False, False),
    )
