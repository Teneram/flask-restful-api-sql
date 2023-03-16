from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm.session import Session
from werkzeug.datastructures import MultiDict

from app.source.utilities import (BaseManager, CourseManager, GroupManager,
                                  StudentManager)
from db.models import CourseModel, GroupModel, StudentModel

test_student_data_1 = {
    "data": [
        {"id": 1, "student_first_name": "Roman", "student_last_name": "Romanovich"},
        {"id": 2, "student_first_name": "Ivan", "student_last_name": "Ivanovich"},
    ]
}
test_student_data_2 = {
    "course": MultiDict([("course", "Math")]),
    "students": [
        {"id": 1, "student_first_name": "Roman", "student_last_name": "Romanovich"},
        {"id": 2, "student_first_name": "Ivan", "student_last_name": "Ivanovich"},
    ],
}


class TestStudentManager:
    @pytest.mark.parametrize(
        "args, expected_result",
        [
            (MultiDict({}), test_student_data_1),
            (MultiDict({"course": "Math"}), test_student_data_2),
        ],
    )
    def test_get_students(
        self,
        test_db: Session,
        args: MultiDict,
        expected_result: Dict[str, Any],
    ):
        with test_db as session:
            student_manager = StudentManager(session)
            students = [
                StudentModel(first_name="Roman", last_name="Romanovich"),
                StudentModel(first_name="Ivan", last_name="Ivanovich"),
            ]
            courses = [CourseModel(name="Math"), CourseModel(name="Biology")]
            session.add_all(students + courses)

            for student in students:
                student.courses = courses

            result = student_manager.get_students(args)

            assert result == expected_result

    def test_add_student(self, test_db: Session):
        args = MultiDict({"first_name": "Roman", "last_name": "Romanovich"})

        with test_db as session:
            student_manager = StudentManager(session)
            result = student_manager.add_student(args)

            assert result == {
                "id": 1,
                "student_first_name": "Roman",
                "student_last_name": "Romanovich",
            }
            assert session.query(StudentModel).count() == 1

    def test_delete_student(self, test_db: Session):
        with test_db as session:
            student_manager = StudentManager(session)
            students = [
                StudentModel(id=1, first_name="Roman", last_name="Romanovich"),
                StudentModel(id=2, first_name="Ivan", last_name="Ivanovich"),
            ]
            session.add_all(students)

            student_manager.delete_student(student_id=1)

            assert session.query(StudentModel).count() == 1
            assert (
                session.query(StudentModel).filter_by(id=2).first().first_name == "Ivan"
            )

    def test_make_student_data(self, test_db: Session):
        with test_db as session:
            students = [
                StudentModel(id=1, first_name="Roman", last_name="Romanovich"),
                StudentModel(id=2, first_name="Ivan", last_name="Ivanovich"),
            ]
            courses = [CourseModel(name="Math"), CourseModel(name="Biology")]
            groups = [GroupModel(name="CN-75")]

            session.add_all(students + courses + groups)

            for student in students:
                student.courses = courses
                student.group = groups[0]

            test_student = session.query(StudentModel).filter_by(id=1).first()
            test_courses = courses
            test_group = GroupManager.main_group_data(test_student)

            result = StudentManager.make_student_data(
                test_student, test_group, test_courses
            )

            expected_result = {
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

            assert result == expected_result

    @patch("app.source.utilities.GroupManager.main_group_data")
    @patch("app.source.utilities.StudentManager.make_student_data")
    def test_get_student(
        self,
        student_data: MagicMock,
        group_data: MagicMock,
        test_db: Session,
    ):
        test_data = {
            "courses": [
                {
                    "id": 10,
                    "course_description": None,
                    "course_name": "Geography",
                }
            ],
            "group": {"id": 1, "group_name": "CT-70"},
            "student": {
                "id": 1,
                "student_first_name": "Roman",
                "student_last_name": "Romanovich",
            },
        }
        student_data.return_value = test_data
        group_data.return_value = "group data"

        with test_db as session:
            student_manager = StudentManager(session)
            students = [StudentModel(id=1, first_name="Roman", last_name="Romanovich")]
            session.add_all(students)

            result = student_manager.get_student(1)

            assert result == test_data
            assert session.query(StudentModel).count() == 1
            assert (
                session.query(StudentModel).filter_by(id=1).first().first_name
                == "Roman"
            )

    @patch("app.source.utilities.random.choice")
    def test_create_students(self, choices: MagicMock):
        choices.side_effect = [
            "Roman",
            "Romanovich",
            "Ivan",
            "Ivanovich",
            "Timur",
            "Timurovich",
        ]
        results = StudentManager.create_students(3)
        expected_results = [
            {
                "id": None,
                "student_first_name": "Roman",
                "student_last_name": "Romanovich",
            },
            {
                "id": None,
                "student_first_name": "Ivan",
                "student_last_name": "Ivanovich",
            },
            {
                "id": None,
                "student_first_name": "Timur",
                "student_last_name": "Timurovich",
            },
        ]

        for result, expected in zip(results, expected_results):
            assert result.__json__() == expected

    @patch("app.source.utilities.random.randrange")
    def test_allocate_to_courses(self, ranges: MagicMock, test_db: Session):
        with test_db as session:
            ranges.side_effect = [2, 2]
            students = [
                StudentModel(id=1, first_name="Roman", last_name="Romanovich"),
                StudentModel(id=2, first_name="Ivan", last_name="Ivanovich"),
            ]
            courses = [CourseModel(name="Math"), CourseModel(name="Biology")]
            StudentManager.allocate_to_courses(courses, students, 2)
            session.add_all(students + courses)

            for count, student in enumerate(students, start=1):
                test_student = session.query(StudentModel).filter_by(id=count).first()
                assert len(test_student.courses) == 2

    @patch("app.source.utilities.random.randint")
    def test_allocate_to_groups(self, randint: MagicMock, test_db: Session):
        with test_db as session:
            randint.return_value = 10
            students = [
                StudentModel(
                    id=count + 1,
                    first_name="some_first_name",
                    last_name="some_last_name",
                )
                for count in range(10)
            ]
            groups = [GroupModel(name="CN-75"), GroupModel(name="SF-65")]
            StudentManager.allocate_to_groups(groups, students)
            session.add_all(students + groups)

            group_1 = session.query(GroupModel).filter_by(id=1).first()
            group_2 = session.query(GroupModel).filter_by(id=2).first()

            assert len(group_1.students) == 10
            assert len(group_2.students) == 0

    def test_change_student_name(self, test_db: Session):
        with test_db as session:
            student_manager = StudentManager(session)
            students = [
                StudentModel(id=1, first_name="Roman", last_name="Romanovich"),
                StudentModel(id=2, first_name="Ivan", last_name="Ivanovich"),
            ]
            session.add_all(students)

            student_manager.change_student_name(1, "Oleg", "Olegovich")

            assert (
                session.query(StudentModel).filter_by(id=1).first().first_name == "Oleg"
            )
            assert (
                session.query(StudentModel).filter_by(id=1).first().last_name
                == "Olegovich"
            )


class TestGroupManager:
    @patch("app.source.utilities.random.choices")
    def test_create_group_name(self, choice: MagicMock):
        choice.side_effect = ["AV", "12"]
        result = GroupManager.create_group_name()
        expected_result = "AV-12"

        assert result == expected_result

    @patch("app.source.utilities.GroupManager.create_group_name")
    def test_create_group_names(self, group_name: MagicMock):
        group_name.side_effect = ["AV-12", "DB-11", "LD-88"]

        result = GroupManager.create_group_names(3)
        expected_result = {"AV-12", "DB-11", "LD-88"}

        assert result == expected_result

    def test_main_group_data(self, test_db: Session):
        with test_db as session:
            group_manager = GroupManager(session)
            students = [
                StudentModel(id=1, first_name="Roman", last_name="Romanovich"),
                StudentModel(id=2, first_name="Ivan", last_name="Ivanovich"),
            ]
            groups = [GroupModel(name="CN-75")]
            for student in students:
                student.group = groups[0]
            session.add_all(students + groups)

            result = group_manager.main_group_data(
                session.query(StudentModel).filter_by(id=1).first()
            )
            expected_result = {"id": 1, "group_name": "CN-75"}

            assert result == expected_result

    def test_get_group_count(self, test_db: Session):
        args = MultiDict({"max_students_count": "2"})

        with test_db as session:
            group_manager = GroupManager(session)
            students = [
                StudentModel(id=1, first_name="Roman", last_name="Romanovich"),
                StudentModel(id=2, first_name="Ivan", last_name="Ivanovich"),
                StudentModel(id=3, first_name="Evgen", last_name="Porilov"),
                StudentModel(id=4, first_name="Alla", last_name="Petrenko"),
            ]
            groups = [GroupModel(name="CN-75"), GroupModel(name="BV-11")]
            for student in students[:3]:
                student.group = groups[0]
            students[3].group = groups[1]
            session.add_all(students + groups)

            result = group_manager.get_group_count(args)
            group, student_count = result[0]

            assert len(result) == 1
            assert group.name == "BV-11"
            assert student_count == 1

    @pytest.mark.parametrize(
        "args, expected_result",
        [
            (
                MultiDict({}),
                {
                    "data": [
                        {"id": 1, "group_name": "CN-75"},
                        {"id": 2, "group_name": "FS-56"},
                        {"id": 3, "group_name": "DS-23"},
                    ]
                },
            ),
            (
                MultiDict({"max_students_count": 3}),
                {
                    "data": [
                        {"group_id": 1, "group_name": "CN-75", "student_count": 2},
                        {"group_id": 2, "group_name": "FS-56", "student_count": 5},
                    ]
                },
            ),
        ],
    )
    def test_get_group_data(
        self,
        test_db: Session,
        args: MultiDict,
        expected_result: Dict[str, List[Dict[str, Any]]],
    ):
        with test_db as session:
            group_manager = GroupManager(session)
            groups = [
                GroupModel(name="CN-75"),
                GroupModel(name="FS-56"),
                GroupModel(name="DS-23"),
            ]
            session.add_all(groups)
            group_counts = [
                (GroupModel(id=1, name="CN-75"), 2),
                (GroupModel(id=2, name="FS-56"), 5),
            ]
            group_data = group_manager.get_group_data(args, group_counts)

            assert group_data == expected_result

    def test_get_group_details(self, test_db: Session):
        with test_db as session:
            group_manager = GroupManager(session)
            groups = [GroupModel(id=1, name="CN-75"), GroupModel(id=2, name="BV-11")]
            session.add_all(groups)

            result = group_manager.get_group_details(1)

            assert result.__json__() == {"id": 1, "group_name": "CN-75"}

    @patch("app.source.utilities.GroupManager.create_group_names")
    def test_create_groups(self, group_names: MagicMock):
        group_names.return_value = ("VB-22", "ER-55")
        results = GroupManager.create_groups(2)
        expected_results = [
            {"id": None, "group_name": "VB-22"},
            {"id": None, "group_name": "ER-55"},
        ]

        for result, expected in zip(results, expected_results):
            assert result.__json__() == expected


class TestCourseManager:
    @patch("app.source.utilities.random.choice")
    def test_allocate_course_random(self, choice: MagicMock, test_db: Session):
        args = MultiDict({})
        with test_db as session:
            course_manager = CourseManager(session)
            choice.return_value = CourseModel(id=1, name="Math")
            students = [
                StudentModel(id=1, first_name="Roman", last_name="Romanovich"),
                StudentModel(id=2, first_name="Ivan", last_name="Ivanovich"),
                StudentModel(id=3, first_name="Evgen", last_name="Porilov"),
                StudentModel(id=4, first_name="Alla", last_name="Petrenko"),
            ]
            session.add_all(students)

            course_manager.allocate_course(1, args)

            student = session.query(StudentModel).filter_by(id=1).first()
            course = student.courses

            assert len(course) == 1
            assert course[0].__json__() == {
                "id": 1,
                "course_name": "Math",
                "course_description": None,
            }

    def test_allocate_course_by_selection(self, test_db: Session):
        args = MultiDict({"course": "Math"})
        with test_db as session:
            course_manager = CourseManager(session)
            students = [
                StudentModel(id=1, first_name="Roman", last_name="Romanovich"),
                StudentModel(id=2, first_name="Ivan", last_name="Ivanovich"),
                StudentModel(id=3, first_name="Evgen", last_name="Porilov"),
                StudentModel(id=4, first_name="Alla", last_name="Petrenko"),
            ]
            courses = [CourseModel(name="Math"), CourseModel(name="Biology")]
            session.add_all(students + courses)

            course_manager.allocate_course(1, args)

            student = session.query(StudentModel).filter_by(id=1).first()
            course = student.courses

            assert len(course) == 1
            assert course[0].__json__() == {
                "id": 1,
                "course_name": "Math",
                "course_description": None,
            }

    def test_delete_course(self, test_db_filled: Session):
        with test_db_filled as session:
            course_manager = CourseManager(session)

            course_manager.delete_course(student_id=1, course_id=1)
            student_1 = session.query(StudentModel).filter_by(id=1).first()
            student_2 = session.query(StudentModel).filter_by(id=2).first()

            assert (len(student_1.courses)) == 1
            assert (len(student_2.courses)) == 2
            assert student_1.courses[0].__json__() == {
                "id": 2,
                "course_name": "Biology",
                "course_description": None,
            }
            assert student_2.courses[0].__json__() == {
                "id": 1,
                "course_name": "Math",
                "course_description": None,
            }

    def test_get_course_details(self, test_db: Session):
        with test_db as session:
            course_manager = CourseManager(session)
            courses = [CourseModel(name="Math"), CourseModel(name="Biology")]
            session.add_all(courses)

            result = course_manager.get_course_details(2)

            assert result.__json__() == {
                "id": 2,
                "course_name": "Biology",
                "course_description": None,
            }

    def test_create_courses(self):
        course_names = ["Math", "Physics", "Biology"]
        results = CourseManager.create_courses(course_names)
        expected_results = [
            {"course_description": None, "id": None, "course_name": "Math"},
            {"course_description": None, "id": None, "course_name": "Physics"},
            {"course_description": None, "id": None, "course_name": "Biology"},
        ]

        for result, expected in zip(results, expected_results):
            assert result.__json__() == expected


class TestBaseManager:
    def test_query_all_data(self, test_db: Session):
        with test_db as session:
            manager = BaseManager(session)
            students = [
                StudentModel(id=1, first_name="Roman", last_name="Romanovich"),
                StudentModel(id=2, first_name="Ivan", last_name="Ivanovich"),
            ]
            session.add_all(students)

            result = manager.query_all_data(StudentModel)
            expected_result = {
                "data": [
                    {
                        "id": 1,
                        "student_first_name": "Roman",
                        "student_last_name": "Romanovich",
                    },
                    {
                        "id": 2,
                        "student_first_name": "Ivan",
                        "student_last_name": "Ivanovich",
                    },
                ]
            }

            assert result == expected_result
