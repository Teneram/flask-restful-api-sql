from sqlalchemy import Column, ForeignKey, Integer

from db.base import Base


class StudentCourseModel(Base):
    __tablename__ = "student_courses"

    student_id = Column(Integer, ForeignKey("students.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
