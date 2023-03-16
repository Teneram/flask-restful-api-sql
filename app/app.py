from flasgger import Swagger
from flask import Flask
from flask_restful import Api
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm.exc import UnmappedInstanceError

from app.source.errors import unmapped_instance, wrong_arguments  # noqa
from constants import VERSION

app = Flask(__name__)
app.register_error_handler(UnmappedInstanceError, unmapped_instance)
app.register_error_handler(AttributeError, unmapped_instance)
app.register_error_handler(ValueError, unmapped_instance)
app.register_error_handler(IndexError, unmapped_instance)
app.register_error_handler(ArgumentError, wrong_arguments)
swagger = Swagger(app)
api = Api(app)


from app.source.views import (CourseDetails, Courses, GroupDetails,  # noqa
                              Groups, StudentCourse, StudentCourses,
                              StudentDetails, Students)

api.add_resource(Students, f"/api/v{VERSION}/students")
api.add_resource(StudentDetails, f"/api/v{VERSION}/students/<student_id>")
api.add_resource(Groups, f"/api/v{VERSION}/groups")
api.add_resource(GroupDetails, f"/api/v{VERSION}/groups/<group_id>")
api.add_resource(Courses, f"/api/v{VERSION}/courses")
api.add_resource(CourseDetails, f"/api/v{VERSION}/courses/<course_id>")
api.add_resource(StudentCourses, f"/api/v{VERSION}/students/<student_id>/courses")
api.add_resource(
    StudentCourse, f"/api/v{VERSION}/students/<student_id>/courses/<course_id>"
)
