from typing import Generator

from sqlalchemy.orm import sessionmaker

from app.source.utilities import CourseManager, GroupManager, StudentManager
from constants import COURSE_NAMES
from db.helpers import get_engine
from db.logger import logging

logger = logging.getLogger("db_creation.py")


def create_session(url) -> Generator:
    logger.info("Session creation called")
    engine = get_engine(url)
    logger.info("Session engine created")

    new_session = sessionmaker(bind=engine)
    session = new_session()
    logger.info("Session created")
    try:
        yield session
    finally:
        session.close()
        logger.info("Session closed")


def db_fill(session) -> None:
    groups = GroupManager.create_groups(10)
    logger.info("Groups data generated")
    courses = CourseManager.create_courses(COURSE_NAMES)
    logger.info("Courses data generated")
    students = StudentManager.create_students(200)
    logger.info("Students data generated")

    StudentManager.allocate_to_courses(courses, students, 3)
    logger.info("Students allocated to course(-s)")
    StudentManager.allocate_to_groups(groups, students)
    logger.info("Students allocated to group(-s)")

    session.add_all(groups + courses + students)
    session.commit()
    logger.info("All data successfully added to the database")
