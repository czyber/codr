
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker


def new_uuid():
    return str(uuid.uuid4())


Base = declarative_base()


class CodebaseModel(Base):
    __tablename__ = 'sql_codebases'
    id: Mapped[str] = mapped_column(primary_key=True, default=new_uuid)
    name: Mapped[str]
    url: Mapped[str | None]
    sha: Mapped[str | None]


engine = create_engine('sqlite:///sqlite.db', echo=True)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
