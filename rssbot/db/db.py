from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from rssbot.db import Base


class Database:
    def __init__(self, db_uri: str):
        engine = create_engine(db_uri, echo=False)
        # self._init_db()

        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine)

