import os

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session

from config import DevelopmentConfig, TestConfig
from db.helpers import get_engine


def configure_session() -> Session:
    env = os.environ.get("FLASK_ENV", "development")

    if env == "testing":
        engine = get_engine(TestConfig.SQLALCHEMY_DATABASE_URI)
    else:
        engine = get_engine(DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    new_session = scoped_session(Session)
    return new_session()


def configure_app(application):
    env = os.environ.get("FLASK_ENV", "development")

    if env == "testing":
        application.config.from_object(TestConfig)
    else:
        application.config.from_object(DevelopmentConfig)

    return application
