import logging
import time

from urllib.parse import urlparse

import html_telegraph_poster
import newspaper
import nltk
import telegram

from html_telegraph_poster.upload_images import upload_image
from sqlalchemy import and_

from rssbot import Database, News


nltk.download("punkt")

logger = logging.getLogger(__name__)


class RSSBot:
    DELAY_BETWEEN_MESSAGES = 5
    PUBLICATION_PAUSE = 0
    POST_MESSAGE = '<b>{title}</b>\n\n<i>via</i> {link}'
    TELEGRAPH_TML_WITHOUT_IMAGE = (
        '{text}<p><i>Source: </i><a href="{link}">{simple_link}</a></p>'
    )
    TELEGRAPH_TML_WITH_IMAGE =(
        '<img src="{img}"/>' + TELEGRAPH_TML_WITHOUT_IMAGE
    )

    def __init__(
        self, token: str, shortener, channel_id: int, source_list: list, db_uri: str
    ):
        self._bot = telegram.Bot(token=token)
        self._channel_id = channel_id
        self._shortener_obj = shortener
        self._rss_source_list = source_list
        self._db = Database(db_uri)

    def _fetch_news(self) -> None:
        logger.info("Updating news by source list")
        all_news = []
        for source in self._rss_source_list:
            try:
                all_news.extend(source.get_news())
            except Exception as ex:
                logger.exception(f"Failed to parse a link: {str(ex)}", exc_info=True)

        for item in all_news:
            if not bool(
                self._db.session.query(News).filter_by(link=item["link"]).first()
            ):
                logger.info(f'A new post has been detected: {item["link"]}')
                now = int(time.mktime(time.localtime()))
                item["publish"] = now + self.PUBLICATION_PAUSE
                # Save to the DB
                self._db.session.add(News(**item))
                self._db.session.commit()

    def _create_telegraph(self, link: str, title: str) -> str:
        logger.info(f"Parsing an article: {link}")
        article = newspaper.Article(link, language="uk")
        article.download()
        article.parse()
        article.nlp()

        parsed_uri = urlparse(link)
        params = {
            'text': ''.join(map(lambda s: f'<p>{s}</p>', article.text.split('\n'))),
            'simple_link': parsed_uri.netloc,
            'link': self._shortener_obj.get_short_link(link),
        }

        telegraph_tmpl = self.TELEGRAPH_TML_WITHOUT_IMAGE

        if article.top_image:
            telegraph_tmpl = self.TELEGRAPH_TML_WITH_IMAGE
            image = upload_image(article.top_image)
            params.update({'img': image})

        telegraph_text = telegraph_tmpl.format(**params)
        telegraph_url = html_telegraph_poster.upload_to_telegraph(
            title=title,
            author="RSS bot",
            text=telegraph_text,
            author_url="https://goo.gl/VNv6M8",
        )

        return telegraph_url['url']

    def publish_news(self) -> None:
        self._fetch_news()
        posts_from_db = (
            self._db.session.query(News)
            .filter(
                and_(
                    News.message_id == 0,
                    News.publish <= int(time.mktime(time.localtime())),
                )
            )
            .all()
        )

        logger.info(f"Selected {len(posts_from_db)} news to post")
        for item in posts_from_db:
            try:
                telegraph_url = self._create_telegraph(item.link, item.title)
                publication = self._bot.sendMessage(
                    chat_id=self._channel_id,
                    text=self.POST_MESSAGE.format(title=item.title, link=telegraph_url),
                    parse_mode=telegram.ParseMode.HTML,
                    disable_notification=True,
                )
                message_id, chat_id = publication.message_id, publication["chat"]["id"]

                # Update message and chat id
                self._db.session.query(News).filter_by(link=item.link).update(
                    {"chat_id": chat_id, "message_id": message_id}
                )
                self._db.session.commit()

                logger.info(f"Posted {message_id} to {chat_id}: {item.link}")

                time.sleep(self.DELAY_BETWEEN_MESSAGES)
            except Exception as ex:
                logger.exception(f"Failed to post a message: {str(ex)}", exc_info=True)

        self._db.session.close()
