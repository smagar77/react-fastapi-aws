import re
import datetime

from sqlalchemy import String, Integer, DateTime, Column, TIMESTAMP, Boolean
from sqlalchemy import func
from sqlalchemy.ext.declarative import as_declarative, declared_attr


class CoreModel:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    modified_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())


@as_declarative()
class Base:
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()


class RDSMonitorCache(Base, CoreModel):
    maintenance_window: str = Column(String(200))
    backup_window: str = Column(String(200))
    automated_backups: str = Column(String(200))
    instance_class: str = Column(String(200))
    storage: str = Column(String(200))
    maximum_storage_threshold: str = Column(String(200))
    multi_az: bool = Column(Boolean)
    account_name: str = Column(String(200))
    instance_identifier: str = Column(String(200))
    instance_status: str = Column(String(200))
    engine: str = Column(String(200))
