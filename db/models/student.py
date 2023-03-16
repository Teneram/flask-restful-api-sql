from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base


class StudentModel(Base):
    __tablename__ = "students"

    id = Column("id", Integer, primary_key=True)
    first_name = Column("first_name", String)
    last_name = Column("last_name", String)
    courses = relationship(
        "CourseModel", secondary="student_courses", back_populates="students"
    )

    group_id = Column(Integer, ForeignKey("groups.id"))
    group = relationship("GroupModel", back_populates="students")

    def __repr__(self):
        return f"({self.id}) {self.first_name} {self.last_name}"

    def __json__(self):
        return {
            "id": self.id,
            "student_first_name": self.first_name,
            "student_last_name": self.last_name,
        }
