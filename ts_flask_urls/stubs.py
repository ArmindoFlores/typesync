import typing

import flask


class Response[_](flask.Response):
    pass


def jsonify[T](data: T) -> Response[T]:
    return typing.cast(Response[T], flask.jsonify(data))
