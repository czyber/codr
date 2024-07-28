import uuid
from datetime import datetime
from typing import List

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def new_uuid():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    __abstract__ = True

    def to_dict(self):
        return {
            field.name: getattr(self, field.name) for field in self.__table__.columns
        }


class CodebaseModel(Base):
    __tablename__ = "codebases"
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
    __tablename__ = "repos"
    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str]
    owner: Mapped[str]


class VersionControlInfoModel(Base):
    __tablename__ = "version_control_info"
    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    access_token: Mapped[str]
    refresh_token: Mapped[str]
    access_token_expires_at: Mapped[datetime]
    refresh_token_expires_at: Mapped[datetime]
    version_control_type: Mapped[str]


user_version_control_info_association_table = Table(
    "user_version_control_info_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("version_control_info_id", ForeignKey("version_control_info.id")),
)


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    username: Mapped[str]
    repos: Mapped[List[RepoModel]] = relationship(
        secondary=user_repo_association_table, cascade="all, delete"
    )
    version_control_infos: Mapped[List[VersionControlInfoModel]] = relationship(
        secondary=user_version_control_info_association_table, cascade="all, delete"
    )
