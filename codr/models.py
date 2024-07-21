
import uuid

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, DeclarativeBase


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


class UserModel(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    username: Mapped[str]
    github_access_token: Mapped[str | None]
