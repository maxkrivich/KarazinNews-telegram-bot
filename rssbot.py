#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2017 Maxim Krivich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import tqdm
import time
import json
import pytz
import config
import logging
import messages
import requests
import telegram
import feedparser

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import Column, Integer, BigInteger, DateTime, String, and_

sched = BlockingScheduler()
Base = declarative_base()


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


class TqdmLoggingHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET):
        super(self.__class__, self).__init__(level)

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.tqdm.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.addHandler(TqdmLoggingHandler())


class Source(object):
    """
    Класс для парсинга RSS-канала.
    Выделяет из общей информации только интереующие поля: Заголовок, ссылку, дату публикации.
    """

    def __init__(self, links):
        self.links = links
        self.news = []
        # self.refresh()

    @classmethod
    def __parse_date(cls, date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass
        return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')

    def refresh(self):
        self.news = []
        current_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
        for i in self.links:
            data = feedparser.parse(i)
            for item in tqdm.tqdm(data['entries'], desc='Getting news %s' % i):
                date = self.__parse_date(
                    item['published']).replace(tzinfo=pytz.UTC)
                if (current_time - date).days < 2:
                    self.news.append(News(title=item['title'],
                                          short_description=item['summary_detail']['value'],
                                          link=item['link'],
                                          date=date))
                    # pprint.pprint(item)
            time.sleep(2)

    def __repr__(self):
        return "<RSS ('%s','%s')>" % (self.links, len(self.news))


class GOOGL(object):
    """
    Класс для работы с api goo.gl
    Этот класс служит сокращение ссылок с помощью сервиса goo.gl
    """
    url = 'https://www.googleapis.com/urlshortener/v1/url?key={at}'

    def __init__(self, access_token):
        self.access_token = access_token

    def short_link(self, long_link):
        payload = {'longUrl': long_link}
        headers = {'Content-type': 'application/json'}
        try:
            r = requests.post(self.url.format(
                at=self.access_token), data=json.dumps(payload), headers=headers)
            if r.status_code == 200:
                return r.json()['id']
            else:
                raise Exception('')
        except Exception:
            return long_link


class Bitly(object):
    """
    Класс для работы с api bitly.com
    Этот класс служит сокращение ссылок с помощью сервиса bitly
    """
    url = 'https://api-ssl.bitly.com/v3/shorten'

    def __init__(self, access_token):
        self.access_token = access_token

    def short_link(self, long_link):
        payload = {'access_token': self.access_token,
                   'format': 'json',
                   'longUrl': long_link,
                   }
        try:
            r = requests.post(self.url, data=payload)
            if r.status_code == 200:
                return json.loads(r.text)['data']['url']
            else:
                raise Exception('')
        except:
            return long_link


class News(Base):
    """
    Класс, описывающий объект новости. Так же, осуществляется взаимодействие с БД.
    Описание полей таблицы ниже.
    """
    __tablename__ = 'KarazinNews'
    # Порядковый номер новости
    id = Column(Integer, primary_key=True)
    # Текст (Заголовок), который будет отправлен в сообщении
    title = Column(String, nullable=False)
    # Краткое описание статьи на сайте
    short_description = Column(String)
    # Ссылка на статью на сайте. Так же отправляется в сообщении
    link = Column(String, nullable=False, unique=True)
    # Дата появления новости на сайте. Носит Чисто информационный характер.
    date = Column(DateTime, nullable=False)
    # Планируемая дата публикации. Сообщение будет отправлено НЕ РАНЬШЕ этой даты. UNIX_TIME.
    publish = Column(BigInteger, nullable=False)
    # Информационный столбец. В данной версии функциональной нагрузки не несет.
    chat_id = Column(BigInteger, nullable=False)
    # Информационный столбец. В данной версии функциональной нагрузки не несет.
    message_id = Column(BigInteger, nullable=False)

    def __init__(self, title, short_description, link, date, publish=0, chat_id=0, message_id=0):
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


@singleton
class Database(object):
    """
    Класс для обработки сессии SQLAlchemy.
    Так же включает в себя минимальный набор методов, вызываемых в управляющем классе.
    """

    def __init__(self, obj):
        engine = create_engine(obj, echo=False)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine)

    def add_news(self, news):
        self.session.add(news)
        self.session.commit()

    def get_post_without_message_id(self):
        return self.session.query(News).filter(and_(News.message_id == 0,
                                                    News.publish <= int(time.mktime(time.localtime())))).all()

    def update(self, link, chat, msg_id):
        self.session.query(News).filter_by(link=link).update(
            {"chat_id": chat, "message_id": msg_id})
        self.session.commit()

    def find_link(self, link):
        return bool(self.session.query(News).filter_by(link=link).first())


class ExportBot(object):
    """
    Класс для работы с Telegram API.
    Реализует основные функции с каналами в telegram: публикация, отслеживание новостей.
    """

    def __init__(self):
        self.pub_pause = config.PUBLICATION_PAUSE
        self.delay_between_messages = config.DELAY_BETWEEN_MESSAGES
        self.db = Database(config.DATABASE_URL)
        self.src = Source(config.NEWS_RESOURCES)
        self.chat_id = config.TELEGRAM_CHAT_ID
        bot_access_token = config.TELEGRAM_ACCESS_TOKEN
        self.bot = telegram.Bot(token=bot_access_token)
        # self.url_shortener = Bitly(config.BITLY_ACCESS_TOKEN)
        self.url_shortener = GOOGL(config.GOOGL_ACCESS_TOKEN)

    def detect(self):
        # получаем 30 последних постов из rss-канала
        self.src.refresh()
        news = self.src.news
        news.reverse()
        # Проверяем на наличие в базе ссылки на новость, если нет, то добавляем в базу данных с
        # отложенной публикацией
        flag = False
        for i in news:
            if not self.db.find_link(i.link):
                now = int(time.mktime(time.localtime()))
                i.publish = now + self.pub_pause
                logger.info('Detect news: %s' % i)
                self.db.add_news(i)
                flag = True
        return flag

    def send_error(self, msg):
        self.bot.sendMessage(chat_id='296266', text=msg)

    def isUpdated(self):
        return len(self.db.get_post_without_message_id()) == 0

    def public_posts(self):
        # Получаем 30 последних записей из rss канала и новости из БД, у которых message_id=0
        current_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
        posts_from_db = self.db.get_post_without_message_id()
        self.src.refresh()
        line = []
        for i in self.src.news:
            if (current_time - i.date).days < 2:
                line.append(i)

        # Выбор пересечний этих списков
        for_publishing = list(set(line) & set(posts_from_db))
        for_publishing = sorted(for_publishing, key=lambda news: news.date)
        # Постинг каждого сообщений
        flag = False
        for post in for_publishing:
            flag = True
            text = messages.POST_MESSAGE.format(title=post.title,
                                                summary=post.short_description,
                                                link=self.url_shortener.short_link(post.link))
            a = self.bot.sendMessage(chat_id=self.chat_id,
                                     text=text,
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=True,
                                     disable_notification=False)
            message_id = a.message_id
            chat_id = a['chat']['id']
            self.db.update(post.link, chat_id, message_id)
            logger.info('Public: %s;%s;' % (post, message_id))
            time.sleep(self.delay_between_messages)
        if flag:
            self.db.session.close()
        return flag


@sched.scheduled_job('interval', minutes=15)
def main():
    try:
        logger.info('Wake up')
        bot = ExportBot()
        if bot.detect() or not bot.isUpdated():
            time.sleep(5)
            while not bot.public_posts():
                pass
        else:
            logger.info('Nothing to post')
        logger.info('Go sleep')
    except Exception as e:
        bot.send_error(e)
        logger.exception(e)


sched.start()

# if __name__ == '__main__':
#     main()
#     db1 = Database(config.DATABASE_URL)
#     db2 = Database(config.DATABASE_URL)
#     print(id(db1), id(db2))
