import datetime
import logging

import feedparser
import pytz


logger = logging.getLogger(__name__)


class RSSSource:
    def __init__(self, link: str):
        self.feed_source = link

    def _parse_date(self, date: str):
        formats = ["%Y-%m-%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S %z"]

        for fmt in formats:
            try:
                return datetime.datetime.strptime(date, fmt)
            except ValueError:
                pass

        return None

    def get_news(self) -> list:
        logger.info(f"Fetching news from {self.feed_source}")
        result = []
        current_time = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        data = feedparser.parse(self.feed_source)
        for item in data["entries"]:
            date = self._parse_date(item["published"])
            if not date:
                continue
            date = date.replace(tzinfo=pytz.UTC)

            if (current_time - date).days < 2:
                result.append(
                    {
                        "title": item["title"],
                        "short_description": item["summary"],
                        "link": item["link"],
                        "date": date,
                    }
                )

        logger.info(f"Fetched {len(result)} items from {self.feed_source}")

        return result
