from sqlalchemy import BigInteger, Column, DateTime, Integer, String

from rssbot.db import Base


class News(Base):
    __tablename__ = "rss_news"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    short_description = Column(String)
    link = Column(String, nullable=False, unique=True)
    date = Column(DateTime, nullable=False)
    publish = Column(BigInteger, nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    message_id = Column(BigInteger, nullable=False)

    def __init__(
        self, title, short_description, link, date, publish=0, chat_id=0, message_id=0
    ):
        self.link = link
        self.title = title
        self.short_description = short_description
        self.date = date
        self.publish = publish
        self.chat_id = chat_id
        self.message_id = message_id

    def _keys(self):
        return (self.title, self.link)

    def __eq__(self, other):
        return self._keys() == other._keys()

    def __hash__(self):
        return hash(self._keys())

    def __repr__(self):
        return "<News ('%s','%s', %s)>" % (self.title, self.link, self.date)
