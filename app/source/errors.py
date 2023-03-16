from http import HTTPStatus

from flask import abort


def unmapped_instance(error):
    abort(HTTPStatus.NOT_FOUND, "The requested resource does not exist")


def wrong_arguments(error):
    abort(HTTPStatus.INTERNAL_SERVER_ERROR, "Server error")
