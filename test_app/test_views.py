from http import HTTPStatus
from typing import Dict, Generator
from unittest.mock import MagicMock, patch
from urllib.parse import urljoin

import pytest
from flask import make_response
from flask.testing import FlaskClient
from sqlalchemy.orm.session import Session

from db.models import CourseModel, StudentModel


class TestStudents:
    url = "/api/v1/students"

    @patch("app.source.views.StudentManager.get_students")
    def test_get_students(
        self,
        get_students: MagicMock,
        client: FlaskClient,
        app_context: Generator,
        testing_env: Generator,
    ) -> None:
        data = {
            "data": [
                {
                    "id": 1,
                    "student_first_name": "Rita",
                    "student_last_name": "Mercalenko",
                },
                {
                    "id": 2,
                    "student_first_name": "Petr",
                    "student_last_name": "Bogolub",
                },
            ]
        }
        get_students.return_value = make_response(data, HTTPStatus.OK)

        response = client.get(self.url)

        assert response.json == data
        assert response.status_code == HTTPStatus.OK

    @patch("app.source.views.StudentManager.get_students")
    def test_get_courses(
        self,
        get_students: MagicMock,
        client: FlaskClient,
        app_context: Generator,
        testing_env: Generator,
    ) -> None:
        data = {
            "course": {"course": "Math"},
            "students": [
                {
                    "id": 1,
                    "student_first_name": "Yaroslava",
                    "student_last_name": "Mercalenko",
                },
                {
                    "id": 2,
                    "student_first_name": "Artem",
                    "student_last_name": "Ostapenko",
                },
            ],
        }
        get_students.return_value = make_response(data, HTTPStatus.OK)

        response = client.get(self.url)

        assert response.json == data
        assert response.status_code == HTTPStatus.OK

    def test_post(
        self,
        client: FlaskClient,
        app_context: Generator,
        test_db_filled: Session,
        testing_env: Generator,
    ) -> None:
        response = client.post(
            urljoin(self.url, f"?first_name=Ivan&last_name=Romanovich")
        )
        test_students = test_db_filled.query(StudentModel).all()
        expected_student = {
            "id": 5,
            "student_first_name": "Ivan",
            "student_last_name": "Romanovich",
        }

        assert response.status_code == HTTPStatus.CREATED
        assert response.json == expected_student
        assert len(test_students) == 5


class TestStudentDetails:
    url = "/api/v1/students/"

    @patch("app.source.views.StudentManager.get_student")
    def test_get(
        self,
        get_student: MagicMock,
        client: FlaskClient,
        app_context: Generator,
        testing_env: Generator,
    ) -> None:
        data = {
            "student": {
                "id": 1,
                "student_first_name": "Roman",
                "student_last_name": "Romanovich",
                "group": {"id": 1, "group_name": "CN-75"},
                "courses": [
                    {"id": 1, "course_name": "Math", "course_description": None},
                    {"id": 2, "course_name": "Biology", "course_description": None},
                ],
            }
        }
        get_student.return_value = data
        response = client.get(urljoin(self.url, "1"))

        assert response.json == data
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize(
        "data, expected_result",
        [
            (
                {"first_name": "Roman", "last_name": "Romanovich"},
                {
                    "message": "Student name have been updated!",
                    "student": {
                        "id": 4,
                        "student_first_name": "Roman",
                        "student_last_name": "Romanovich",
                    },
                },
            ),
            ({"first_name": "", "last_name": ""}, {"message": "Nothing to update"}),
        ],
    )
    def test_patch(
        self,
        data: Dict[str, str],
        expected_result: Dict[str, str],
        client: FlaskClient,
        app_context: Generator,
        test_db_filled: Session,
        testing_env: Generator,
    ) -> None:
        response = client.patch(urljoin(self.url, "4"), json=data)

        assert response.status_code == HTTPStatus.OK
        assert response.json == expected_result

    @pytest.mark.parametrize(
        "student_id, expected_result, status_code",
        [
            ("1", {"message": "Student deleted successfully!"}, HTTPStatus.OK),
            (
                "6",
                {"message": "The requested resource does not exist"},
                HTTPStatus.NOT_FOUND,
            ),
        ],
    )
    def test_delete(
        self,
        student_id: str,
        expected_result: Dict[str, str],
        status_code: HTTPStatus,
        client: FlaskClient,
        app_context: Generator,
        test_db_filled: Session,
        testing_env: Generator,
    ) -> None:
        response = client.delete(urljoin(self.url, student_id))

        assert response.status_code == status_code
        assert response.json == expected_result


class TestGroups:
    url = "/api/v1/groups"

    def test_get_groups(
        self,
        client: FlaskClient,
        app_context: Generator,
        test_db_filled: Session,
        testing_env: Generator,
    ) -> None:
        expected_result = {
            "data": [{"group_name": "CN-75", "id": 1}, {"group_name": "BV-11", "id": 2}]
        }

        response = client.get(self.url)

        assert response.json == expected_result
        assert response.status_code == HTTPStatus.OK

    def test_get_groups_count(
        self,
        client: FlaskClient,
        app_context: Generator,
        test_db_filled: Session,
        testing_env: Generator,
    ) -> None:
        data = {
            "data": [
                {"group_id": 2, "group_name": "BV-11", "student_count": 1},
                {"group_id": 1, "group_name": "CN-75", "student_count": 2},
            ]
        }

        response = client.get(urljoin(self.url, "?max_students_count=2"))

        assert response.json == data
        assert response.status_code == HTTPStatus.OK


class TestGroupDetails:
    url = "/api/v1/groups/"

    @pytest.mark.parametrize(
        "requested_id, expected_result, status_code",
        [
            ("1", {"group_name": "CN-75", "id": 1}, HTTPStatus.OK),
            (
                "11",
                {"message": "Group with given id does not found"},
                HTTPStatus.NOT_FOUND,
            ),
        ],
    )
    def test_get(
        self,
        requested_id: str,
        expected_result: Dict,
        status_code: HTTPStatus,
        client: FlaskClient,
        app_context: Generator,
        test_db_filled: Session,
        testing_env: Generator,
    ) -> None:

        response = client.get(urljoin(self.url, requested_id))

        assert response.json == expected_result
        assert response.status_code == status_code


class TestCourses:
    url = "/api/v1/courses"

    def test_get(
        self,
        client: FlaskClient,
        app_context: Generator,
        test_db_filled: Session,
        testing_env: Generator,
    ) -> None:
        data = {
            "data": [
                {"course_description": None, "course_name": "Math", "id": 1},
                {"course_description": None, "course_name": "Biology", "id": 2},
            ]
        }

        response = client.get(self.url)

        assert response.json == data
        assert response.status_code == HTTPStatus.OK


class TestCourseDetails:
    url = "/api/v1/courses/"

    @pytest.mark.parametrize(
        "requested_id, expected_result, status_code",
        [
            (
                "1",
                {"course_description": None, "course_name": "Math", "id": 1},
                HTTPStatus.OK,
            ),
            (
                "12",
                {"message": "Course with given id does not found"},
                HTTPStatus.NOT_FOUND,
            ),
        ],
    )
    def test_get(
        self,
        requested_id: str,
        expected_result: Dict,
        status_code: HTTPStatus,
        client: FlaskClient,
        app_context: Generator,
        test_db_filled: Session,
        testing_env: Generator,
    ) -> None:

        response = client.get(urljoin(self.url, requested_id))

        assert response.json == expected_result
        assert response.status_code == status_code


class TestStudentCourses:
    def test_post(
        self,
        client: FlaskClient,
        app_context: Generator,
        test_db: Session,
        testing_env: Generator,
    ) -> None:
        with test_db as session:

            students = [
                StudentModel(id=1, first_name="Roman", last_name="Romanovich"),
                StudentModel(id=2, first_name="Ivan", last_name="Ivanovich"),
                StudentModel(id=3, first_name="Evgen", last_name="Porilov"),
                StudentModel(id=4, first_name="Alla", last_name="Petrenko"),
            ]
            courses = [
                CourseModel(id=1, name="Math"),
                CourseModel(id=2, name="Biology"),
            ]
            session.add_all(students + courses)
            session.commit()

            response = client.post("/api/v1/students/1/courses")
            student = session.query(StudentModel).filter_by(id=1).first()

            assert response.status_code == HTTPStatus.OK
            assert response.json == {"message": "Course added successfully!"}
            assert len(student.courses) == 1


class TestStudentCourse:
    def test_delete(
        self,
        client: FlaskClient,
        app_context: Generator,
        test_db: Session,
        testing_env: Generator,
    ) -> None:
        with test_db as session:
            students = [
                StudentModel(id=1, first_name="Roman", last_name="Romanovich"),
                StudentModel(id=2, first_name="Ivan", last_name="Ivanovich"),
                StudentModel(id=3, first_name="Evgen", last_name="Porilov"),
                StudentModel(id=4, first_name="Alla", last_name="Petrenko"),
            ]
            courses = [
                CourseModel(id=1, name="Math"),
                CourseModel(id=2, name="Biology"),
            ]
            for student in students:
                student.courses = courses
            session.add_all(students + courses)
            session.commit()

            response = client.delete("/api/v1/students/1/courses/1")
            student = session.query(StudentModel).filter_by(id=1).first()

            assert response.status_code == HTTPStatus.OK
            assert (len(student.courses)) == 1
            assert response.json == {"message": "Course deleted successfully!"}
            assert student.courses[0].__json__() == {
                "id": 2,
                "course_name": "Biology",
                "course_description": None,
            }
