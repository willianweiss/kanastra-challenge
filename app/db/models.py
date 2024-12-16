import uuid
from enum import Enum as PyEnum

from sqlalchemy import Column, Date, Enum, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DebtStatus(PyEnum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Debt(Base):
    __tablename__ = "debt"

    debt_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    government_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    debt_amount = Column(Float, nullable=False)
    debt_due_date = Column(Date, nullable=False)
    status = Column(Enum(DebtStatus), nullable=False)
