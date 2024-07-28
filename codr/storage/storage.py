from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from codr.models import Base

engine = create_engine("sqlite:///sqlite.db", echo=True)

SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
