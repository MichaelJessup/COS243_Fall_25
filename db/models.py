from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel

class Set(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    cards: list["Card"] = Relationship(back_populates="set")

class Card(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    front: str
    back: str
    set_id: int | None = Field(default=None, foreign_key="set.id")
    set: Set | None = Relationship(back_populates="cards")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str