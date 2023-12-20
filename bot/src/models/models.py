from typing import Optional

from pydantic import PositiveInt
from sqlalchemy import Column, BIGINT, VARCHAR
from sqlmodel import SQLModel, Field

__all__ = [
    "User",
]


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: PositiveInt = Field(
        default=...,
        sa_column=Column(BIGINT, primary_key=True)
    )
    wallet_address: Optional[str] = Field(
        default=None,
        sa_column=Column(VARCHAR(length=256), nullable=True, unique=True)
    )
    wallet_key: Optional[str] = Field(
        default=None,
        sa_column=Column(VARCHAR(length=256), nullable=True, unique=True)
    )
