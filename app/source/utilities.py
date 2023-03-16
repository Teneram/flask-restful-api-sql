import random
import string
from typing import Any, Dict, List, Optional, Set

from sqlalchemy import func
from werkzeug.datastructures import MultiDict

from constants import FIRST_NAMES, LAST_NAMES
from db.models import CourseModel, GroupModel, StudentModel


class BaseManager:
    def __init__(self, session):
        self.session = session

    def query_all_data(self, model: Any) -> Dict[str, List[Dict[str, Any]]]:
        data: Dict[str, List[Dict[str, Any]]] = {"data": []}
        entities = self.session.query(model)
        for entity in entities:
            data["data"].append(entity.__json__())
        return data


class StudentManager(BaseManager):
    def get_students(self, args: MultiDict) -> Dict[str, Any]:
        if args.get("course"):
            course_ = (
                self.session.query(CourseModel)
                .filter_by(name=args.get("course"))
                .first()
            )
            students_in_group = course_.students
            data: Dict[str, Any] = {"course": args, "students": []}
            for student in students_in_group:
                data["students"].append(student.__json__())
        else:
            data = self.query_all_data(StudentModel)

        return data

    def add_student(self, args: MultiDict) -> Dict[str, Any]:
        record = StudentModel(
            first_name=args.get("first_name"), last_name=args.get("last_name")
        )
        self.session.add(record)
        new_student = (
            self.session.query(StudentModel).order_by(StudentModel.id.desc()).first()
        )
        self.session.commit()
        return new_student.__json__()

    def delete_student(self, student_id: int) -> None:
        student = self.session.query(StudentModel).filter_by(id=student_id).first()
        self.session.delete(student)
        self.session.commit()

    @staticmethod
    def make_student_data(
        student: StudentModel, group: Dict[str, Optional[str]], courses
    ) -> Dict[str, Any]:
        data = {"student": student.__json__()}
        data["student"].update({"group": group})
        data["student"].update({"courses": []})
        for course in courses:
            data["student"]["courses"].append(course.__json__())
        return data

    def get_student(self, student_id: int) -> Dict[str, Any]:
        student = self.session.query(StudentModel).filter_by(id=student_id).first()
        courses = student.courses
        group = GroupManager.main_group_data(student)
        data = StudentManager.make_student_data(student, group, courses)
        return data

    def change_student_name(
        self,
        student_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> Dict[str, Any]:
        student = self.session.query(StudentModel).filter_by(id=student_id).first()
        if first_name:
            student.first_name = first_name
        if last_name:
            student.last_name = last_name
        self.session.commit()

        return student.__json__()

    @staticmethod
    def create_students(amount: int) -> List[StudentModel]:
        students = [
            StudentModel(
                first_name=random.choice(FIRST_NAMES),
                last_name=random.choice(LAST_NAMES),
            )
            for _ in range(1, amount + 1)
        ]
        return students

    @staticmethod
    def allocate_to_courses(
        courses: List[CourseModel], students: List[StudentModel], amount: int
    ) -> None:
        if amount in range(1, len(courses) + 1):
            for student in students:
                student.courses = random.sample(
                    courses, k=random.randrange(1, amount + 1)
                )

    @staticmethod
    def allocate_to_groups(
        groups: List[GroupModel], students: List[StudentModel]
    ) -> None:
        for group in groups:
            if len(students) >= 10:
                for student in students[: random.randint(10, 30)]:
                    student.group = group
                    students.pop(students.index(student))


class GroupManager(BaseManager):
    @staticmethod
    def create_group_name() -> str:
        return (
            "".join(random.choices(string.ascii_uppercase, k=2))
            + "-"
            + "".join(random.choices(string.digits, k=2))
        )

    @staticmethod
    def create_group_names(amount: int) -> Set[str]:
        group_names: Set[str] = set()
        while len(group_names) < amount:
            group_names.add(GroupManager.create_group_name())
        return group_names

    @staticmethod
    def create_groups(amount: int) -> List[GroupModel]:
        groups = [
            GroupModel(name=group) for group in GroupManager.create_group_names(amount)
        ]
        return groups

    @staticmethod
    def main_group_data(student: StudentModel) -> Dict[str, Optional[str]]:
        group: Dict[str, Optional[str]] = {"group_name": None, "group_id": None}
        if student.group:
            group = student.group.__json__()
        return group

    def get_group_count(self, args: MultiDict) -> Any:
        if args.get("max_students_count"):
            group_counts = (
                self.session.query(GroupModel, func.count(StudentModel.id))
                .join(GroupModel.students)
                .group_by(GroupModel.id)
                .having(func.count(StudentModel.id) <= args.get("max_students_count"))
                .all()
            )
            return group_counts

    def get_group_data(
        self, args: MultiDict, group_counts: Any
    ) -> Dict[str, List[Dict[str, Any]]]:
        if args.get("max_students_count"):
            data: Dict[str, List[Dict[str, Any]]] = {"data": []}
            for group, student_count in group_counts:
                data["data"].append(
                    {
                        "group_id": group.id,
                        "group_name": group.name,
                        "student_count": student_count,
                    }
                )
        else:
            data = self.query_all_data(GroupModel)
        return data

    def get_group_details(self, group_id: int) -> Optional[GroupModel]:
        return self.session.query(GroupModel).filter_by(id=group_id).first()


class CourseManager(BaseManager):
    def allocate_course(self, student_id: int, args: MultiDict) -> None:
        student = self.session.query(StudentModel).filter_by(id=student_id).first()

        if args.get("course"):
            course = (
                self.session.query(CourseModel)
                .filter_by(name=args.get("course"))
                .first()
            )
            student.courses.append(course)
        else:
            courses = (
                self.session.query(CourseModel)
                .filter(~CourseModel.students.contains(student))
                .all()
            )
            student.courses.append(random.choice(courses))

        self.session.commit()

    def delete_course(self, student_id: int, course_id: int) -> None:
        student = self.session.query(StudentModel).filter_by(id=student_id).first()
        course = self.session.query(CourseModel).filter_by(id=course_id).first()
        student.courses.remove(course)
        self.session.commit()

    def get_course_details(self, course_id: int) -> Optional[CourseModel]:
        return self.session.query(CourseModel).filter_by(id=course_id).first()

    @staticmethod
    def create_courses(course_names: List[str]) -> List[CourseModel]:
        courses = [CourseModel(name=course) for course in course_names]
        return courses
