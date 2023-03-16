from http import HTTPStatus
from typing import Any, Dict

from flasgger import swag_from
from flask import Response, abort, make_response, request
from flask_restful import Resource

from app.session_generator import generate_session
from app.source.utilities import (BaseManager, CourseManager, GroupManager,
                                  StudentManager)
from db.models import CourseModel


class Students(Resource):
    @swag_from("swagger/students_get.yaml")
    def get(self) -> Response:
        session = next(generate_session())
        args = request.args
        manager = StudentManager(session)
        data = manager.get_students(args)
        response = make_response(data, HTTPStatus.OK)
        return response

    @swag_from("swagger/students_post.yaml")
    def post(self) -> Response:
        session = next(generate_session())
        args = request.args
        manager = StudentManager(session)
        data = manager.add_student(args)
        response = make_response(data, HTTPStatus.CREATED)
        return response


class StudentDetails(Resource):
    @swag_from("swagger/student_details_get.yaml")
    def get(self, student_id: int) -> Response:
        session = next(generate_session())
        manager = StudentManager(session)
        data = manager.get_student(student_id)
        response = make_response(data, HTTPStatus.OK)
        return response

    @swag_from("swagger/student_details_patch.yaml")
    def patch(self, student_id: int) -> Response:
        session = next(generate_session())
        data = request.json
        message: Dict[str, Any] = {"message": "Nothing to update"}

        if data["first_name"] or data["last_name"]:  # type: ignore
            student_manager = StudentManager(session)
            data = student_manager.change_student_name(
                student_id, data["first_name"], data["last_name"]  # type: ignore
            )
            message = {"message": "Student name have been updated!", "student": data}

        response = make_response(message, HTTPStatus.OK)
        return response

    @swag_from("swagger/students_delete.yaml")
    def delete(self, student_id: int) -> Response:
        session = next(generate_session())
        manager = StudentManager(session)
        manager.delete_student(student_id)
        return make_response(
            {"message": "Student deleted successfully!"}, HTTPStatus.OK
        )


class Groups(Resource):
    @swag_from("swagger/groups_get.yaml")
    def get(self) -> Response:
        session = next(generate_session())
        args = request.args
        manager = GroupManager(session)
        group_counts = manager.get_group_count(args)
        data = manager.get_group_data(args, group_counts)
        response = make_response(data, HTTPStatus.OK)
        return response


class GroupDetails(Resource):
    @swag_from("swagger/group_details_get.yaml")
    def get(self, group_id: int) -> Response:
        session = next(generate_session())
        manager = GroupManager(session)
        group = manager.get_group_details(group_id)
        if group:
            return make_response(group.__json__(), HTTPStatus.OK)
        else:
            abort(HTTPStatus.NOT_FOUND, "Group with given id does not found")


class Courses(Resource):
    @swag_from("swagger/courses_get.yaml")
    def get(self) -> Response:
        session = next(generate_session())
        manager = BaseManager(session)
        data = manager.query_all_data(CourseModel)
        response = make_response(data, HTTPStatus.OK)
        return response


class CourseDetails(Resource):
    @swag_from("swagger/course_details_get.yaml")
    def get(self, course_id: int) -> Response:
        session = next(generate_session())
        manager = CourseManager(session)
        course = manager.get_course_details(course_id)
        if course:
            return make_response(course.__json__(), HTTPStatus.OK)
        else:
            abort(HTTPStatus.NOT_FOUND, "Course with given id does not found")


class StudentCourses(Resource):
    @swag_from("swagger/student_courses_post.yaml")
    def post(self, student_id: int) -> Response:
        args = request.args
        session = next(generate_session())
        course_manager = CourseManager(session)
        course_manager.allocate_course(student_id, args)
        response = make_response(
            {"message": "Course added successfully!"}, HTTPStatus.OK
        )
        return response


class StudentCourse(Resource):
    @swag_from("swagger/student_details_delete.yaml")
    def delete(self, student_id: int, course_id: int) -> Response:
        session = next(generate_session())
        manager = CourseManager(session)
        manager.delete_course(student_id, course_id)
        return make_response({"message": "Course deleted successfully!"}, HTTPStatus.OK)
