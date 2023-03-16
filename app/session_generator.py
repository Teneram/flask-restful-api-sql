from app.configurators import configure_session
from db.logger import logging

logger = logging.getLogger(__name__)


def generate_session():
    # create a new session for this request
    session = configure_session()
    logger.info("New session created")
    try:
        yield session

    finally:
        # close the session when the generator is finished
        session.close()
        logger.info("Session closed")
