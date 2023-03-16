from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from db.base import Base


class CourseModel(Base):
    __tablename__ = "courses"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    description = Column("description", Text, default=None)
    students = relationship(
        "StudentModel", secondary="student_courses", back_populates="courses"
    )

    def __repr__(self):
        return f"({self.id}) {self.name}"

    def __json__(self):
        return {
            "id": self.id,
            "course_name": self.name,
            "course_description": self.description,
        }
