from sqlalchemy import Engine, create_engine
from sqlalchemy_utils import create_database, database_exists


def get_engine(project_url: str) -> Engine:
    if not database_exists(project_url):
        create_database(project_url)
    engine = create_engine(project_url, pool_size=50, echo=False)
    return engine
