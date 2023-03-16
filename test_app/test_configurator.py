import os
from unittest import mock

from flask import Flask
from sqlalchemy.orm import Session

from app.configurators import configure_app, configure_session
from config import DevelopmentConfig, TestConfig


@mock.patch.dict(os.environ, {"FLASK_ENV": "development"})
def test_configure_session_development(database_uri):
    session = configure_session()
    engine_url = str(session.bind.engine.url)
    password = session.bind.engine.url.password
    engine_url = engine_url.replace(":***@", f":{password}@")

    assert isinstance(session, Session)
    assert DevelopmentConfig.SQLALCHEMY_DATABASE_URI == engine_url


def test_configure_session_testing(testing_env):
    session = configure_session()
    engine_url = str(session.bind.engine.url)
    password = session.bind.engine.url.password
    engine_url = engine_url.replace(":***@", f":{password}@")

    assert isinstance(session, Session)
    assert TestConfig.SQLALCHEMY_DATABASE_URI == engine_url


@mock.patch.dict(os.environ, {"FLASK_ENV": "development"})
def test_configure_app_development():
    application = Flask(__name__)
    app = configure_app(application)

    assert app.config["DEBUG"] is True
    assert app.config["SQLALCHEMY_DATABASE_URI"] == os.environ["DATABASE_DEV_URI"]


def test_configure_app_testing(testing_env):
    application = Flask(__name__)
    app = configure_app(application)

    assert app.config["DEBUG"] is True
    assert app.config["SQLALCHEMY_DATABASE_URI"] == os.environ["DATABASE_TEST_URI"]
