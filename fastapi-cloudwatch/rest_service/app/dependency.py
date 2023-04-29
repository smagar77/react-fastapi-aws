import inject
import logging
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from rest_service.settings import Settings


logger = logging.getLogger(__name__)


@lru_cache
def get_settings():
    return Settings()


def sql_alchemy_session_factory() -> sessionmaker:
    """"
    SQLAlchemy Session Maker
    """
    settings = get_settings()
    engine = create_engine(
        settings.sqlalchemy_uri,
        pool_size=20
    )
    logger.info("Initializing SQLAlchemy Session Maker")
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def configure_dependency(binder: inject.Binder):
    # bind instances
    binder.bind(Settings, get_settings())

    # Always return the new SQLAlchemy Session
    binder.bind_to_provider(Session, sql_alchemy_session_factory())


inject.configure(configure_dependency)
