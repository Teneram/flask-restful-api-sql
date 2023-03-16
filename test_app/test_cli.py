import os
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm.session import Session
from sqlalchemy_utils import database_exists
from typer.testing import CliRunner

from cli.__main__ import app, create_db, fill_db
from cli.logic import create_session, db_fill
from config import TestConfig
from db.models import CourseModel, GroupModel, StudentModel


def test_create_session():
    url_object = os.environ["DATABASE_TEST_URI"]
    sessions = create_session(url_object)

    for session in sessions:
        engine_url = str(session.bind.engine.url)
        password = session.bind.engine.url.password
        engine_url = engine_url.replace(":***@", f":{password}@")

        assert engine_url == url_object
        assert session is not None


@patch("cli.logic.GroupManager.create_groups")
@patch("cli.logic.CourseManager.create_courses")
@patch("cli.logic.StudentManager.create_students")
def test_db_fill(
    students_mock: MagicMock,
    courses_mock: MagicMock,
    groups_mock: MagicMock,
    test_db: Session,
):
    with test_db as session:
        students_mock.return_value = [
            StudentModel(
                id=count + 1, first_name="some_first_name", last_name="some_last_name"
            )
            for count in range(10)
        ]
        courses_mock.return_value = [
            CourseModel(name="Math"),
            CourseModel(name="Biology"),
            CourseModel(name="History"),
        ]
        groups_mock.return_value = [GroupModel(name="CN-75")]

        db_fill(session)

        group = session.query(GroupModel).filter_by(id=1).first()
        group_expected = {"id": 1, "group_name": "CN-75"}
        groups = session.query(GroupModel).all()

        course = session.query(CourseModel).filter_by(id=1).first()
        course_keys = [key for key in course.__json__()]
        course_keys_expected = ["id", "course_name", "course_description"]
        courses = session.query(CourseModel).all()

        student = session.query(StudentModel).filter_by(id=1).first()
        student_expected = {
            "id": 1,
            "student_first_name": "some_first_name",
            "student_last_name": "some_last_name",
        }
        students = session.query(StudentModel).all()

        student_courses = student.courses
        student_group = student.group

        assert group.__json__() == group_expected
        assert len(groups) == 1
        assert course_keys == course_keys_expected
        assert len(courses) == 3
        assert student.__json__() == student_expected
        assert len(students) == 10
        assert 1 <= len(student_courses) <= 3
        assert student_group.__json__() == group_expected


@pytest.mark.parametrize("command", ["create-db", "fill-db"])
def test_cli_runner(database_uri, command, test_db: Session):
    clirunner = CliRunner()
    result = clirunner.invoke(app, [command])
    assert result.exit_code == 0


def test_create_db(database_uri):
    create_db()
    assert database_exists(TestConfig.SQLALCHEMY_DATABASE_URI)


def test_fill_db(database_uri, test_db: Session):
    with test_db as session:
        fill_db()
        students = session.query(StudentModel).all()
        courses = session.query(CourseModel).all()
        groups = session.query(GroupModel).all()

        student = test_db.query(StudentModel).filter_by(id=1).first()
        course = student.courses
        group = student.group

        assert len(students) == 200
        assert len(courses) == 10
        assert len(groups) == 10
        assert len(course) >= 1
        assert group is not None
