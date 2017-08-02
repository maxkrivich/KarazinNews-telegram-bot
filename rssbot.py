#! venv/bin/python3
# -*- coding: utf-8 -*-

"""

MIT License

Copyright (c) 2017 Max Krivich

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
import os.path
import logging
import requests
import telegram
import feedparser
import configparser

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, DateTime, String, ForeignKey, update, and_

Base = declarative_base()


class Source(object):
    """
    Класс для парсинга RSS-канала.
    Выделяет из общей информации только интереующие поля: Заголовок, ссылку, дату публикации.
    """

    def __init__(self, config_links):
        self.links = [config_links[i] for i in config_links]
        self.news = []
        # self.refresh()

    def refresh(self):
        self.news = []
        for i in self.links:
            data = feedparser.parse(i)
            for item in data['entries']:  # tqdm
                self.news.append(News(title=item['title'],
                                      short_description=item['summary_detail']['value'],
                                      link=item['link'],
                                      date=datetime.strptime(item['published'], '%Y-%m-%d %H:%M:%S')))

            time.sleep(2)

    def __repr__(self):
        return "<RSS ('%s','%s')>" % (self.links, len(self.news))


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
    title = Column(String)
    # Краткое описание статьи на сайте
    short_description = Column(String)
    # Ссылка на статью на сайте. Так же отправляется в сообщении
    link = Column(String)
    # Дата появления новости на сайте. Носит Чисто информационный характер.
    date = Column(DateTime)
    # Планируемая дата публикации. Сообщение будет отправлено НЕ РАНЬШЕ этой даты. UNIX_TIME.
    publish = Column(Integer)
    # Информационный столбец. В данной версии функциональной нагрузки не несет.
    chat_id = Column(Integer)
    # Информационный столбец. В данной версии функциональной нагрузки не несет.
    message_id = Column(Integer)

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
        return self.session.query(News).filter_by(link=link).first() is not None


class ExportBot(object):
    """
    Класс для работы с Telegram API.
    Реализует основные функции с каналами в telegram: публикация, отслеживание новостей.
    """

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('./configs')
        log_file = config['Export_params']['log_file']
        self.pub_pause = int(config['Export_params']['pub_pause'])
        self.delay_between_messages = int(
            config['Export_params']['delay_between_messages'])
        logging.basicConfig(
            format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG, filename='%s' % log_file)
        self.db = Database(config['Database']['path'])
        self.src = Source(config['RSS'])
        self.chat_id = config['Telegram']['chat_id']
        bot_access_token = config['Telegram']['access_token']
        self.bot = telegram.Bot(token=bot_access_token)
        self.bit_ly = Bitly(config['Bitly']['access_token'])

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
                logging.info('Detect news: %s' % i)
                self.db.add_news(i)
                flag = True
        return flag

    def public_posts(self):
        # Получаем 30 последних записей из rss канала и новости из БД, у которых message_id=0
        posts_from_db = self.db.get_post_without_message_id()
        self.src.refresh()
        line = [i for i in self.src.news]
        # Выбор пересечний этих списков
        for_publishing = list(set(line) & set(posts_from_db))
        for_publishing = sorted(for_publishing, key=lambda news: news.date)
        # Постинг каждого сообщений
        flag = False
        for post in for_publishing:
            flag = True
            text = '<b>%s</b>\n%s\n%s' % (post.title, post.short_description,
                                          self.bit_ly.short_link(post.link))
            a = self.bot.sendMessage(chat_id=self.chat_id,
                                     text=text,
                                     parse_mode=telegram.ParseMode.HTML,
                                     disable_web_page_preview=True,
                                     disable_notification=True)
            message_id = a.message_id
            chat_id = a['chat']['id']
            self.db.update(post.link, chat_id, message_id)
            logging.info('Public: %s;%s;' % (post, message_id))
            time.sleep(self.delay_between_messages)
        return flag


def main():
    while True:
        try:
            bot = ExportBot()
            while True:
                if bot.detect():
                    logging.info('Updating news...')
                    time.sleep(10)
                    while not bot.public_posts():
                        pass
                else:
                    logging.info('Nothing to post')
                logging.info('Go sleep')
                time.sleep(5 * 60 * 60)  # sleep 5 hours
        except Exception as e:
            logging.debug(e)


if __name__ == '__main__':
    main()
