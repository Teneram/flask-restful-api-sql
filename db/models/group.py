from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base


class GroupModel(Base):
    __tablename__ = "groups"

    id = Column("id", Integer, primary_key=True)
    name = Column("name", String)
    students = relationship("StudentModel", back_populates="group")

    def __repr__(self):
        return f"({self.id}) {self.name}"

    def __json__(self):
        return {"id": self.id, "group_name": self.name}
