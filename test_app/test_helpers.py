import os

from sqlalchemy.engine import Engine
from sqlalchemy_utils import database_exists, drop_database

from config import TestConfig
from db.helpers import get_engine


def test_get_engine():
    result = get_engine(os.environ["DATABASE_TEST_URI"])

    assert isinstance(result, Engine)
    assert database_exists(os.environ["DATABASE_TEST_URI"]) is True


def test_get_engine_no_db():
    if database_exists(TestConfig.SQLALCHEMY_DATABASE_URI):
        drop_database(TestConfig.SQLALCHEMY_DATABASE_URI)
    result = get_engine(os.environ["DATABASE_TEST_URI"])

    assert isinstance(result, Engine)
    assert database_exists(os.environ["DATABASE_TEST_URI"]) is True
