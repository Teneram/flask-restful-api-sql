import os


class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_DEV_URI"]


class TestConfig:
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_TEST_URI"]
