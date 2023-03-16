import typer

from cli.logic import create_session, db_fill
from config import DevelopmentConfig
from db.base import Base
from db.helpers import get_engine
from db.logger import logging

logger = logging.getLogger("logic.py")

app = typer.Typer()


@app.command()
def create_db() -> None:
    logger.info("Database creation initialized")
    engine = get_engine(DevelopmentConfig.SQLALCHEMY_DATABASE_URI)

    Base.metadata.create_all(bind=engine)
    logger.info("Database created")


@app.command()
def fill_db():
    logger.info("Adding data to the database initialized")
    new_session = create_session(DevelopmentConfig.SQLALCHEMY_DATABASE_URI)
    for session in new_session:
        db_fill(session)
        logger.info("Data added to the database")


if __name__ == "__main__":
    app()
