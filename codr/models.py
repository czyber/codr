from typing import List
import uuid

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.dialects.sqlite import JSON

def new_uuid():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    __abstract__ = True

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.columns}


class CodebaseModel(Base):
    __tablename__ = 'codebases'
    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column()
    name: Mapped[str]
    url: Mapped[str | None]
    sha: Mapped[str | None]


user_repo_association_table = Table(
    "user_repo_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("repo_id", ForeignKey("repos.id")),
)


class RepoModel(Base):
    __tablename__ = 'repos'
    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str]
    owner: Mapped[str]


class UserModel(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    username: Mapped[str]
    github_access_token: Mapped[str | None]
    repos: Mapped[List[RepoModel]] = relationship(secondary=user_repo_association_table, cascade="all, delete")






