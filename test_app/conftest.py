import os
from typing import Generator

import pytest
from flask.testing import FlaskClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session, close_all_sessions

from app.app import app
from config import DevelopmentConfig, TestConfig
from db.base import Base
from db.helpers import get_engine
from db.models import CourseModel, GroupModel, StudentModel


@pytest.fixture()
def test_db() -> Session:
    engine = get_engine(TestConfig.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(bind=engine)
    yield session
    close_all_sessions()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def test_db_filled(test_db) -> Session:
    students = [
        StudentModel(first_name="Roman", last_name="Romanovich"),
        StudentModel(first_name="Ivan", last_name="Ivanovich"),
        StudentModel(first_name="Evgen", last_name="Porilov"),
        StudentModel(first_name="Alla", last_name="Petrenko"),
    ]
    groups = [GroupModel(name="CN-75"), GroupModel(name="BV-11")]
    courses = [CourseModel(name="Math"), CourseModel(name="Biology")]
    for student in students[:2]:
        student.group = groups[0]
        student.courses = courses

    students[3].group = groups[1]
    students[3].courses = courses

    test_db.add_all(students + groups + courses)
    test_db.commit()
    yield test_db


@pytest.fixture()
def my_app() -> Generator:
    app.config.from_object(TestConfig)
    yield app


@pytest.fixture()
def client(my_app: Generator) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def app_context() -> Generator:
    with app.app_context():
        yield


@pytest.fixture()
def database_uri(monkeypatch) -> Generator:
    monkeypatch.setattr(
        DevelopmentConfig, "SQLALCHEMY_DATABASE_URI", os.environ["DATABASE_TEST_URI"]
    )
    yield
    monkeypatch.undo()


@pytest.fixture()
def testing_env(monkeypatch) -> Generator:
    monkeypatch.setenv("FLASK_ENV", "testing")
    yield
    monkeypatch.undo()
