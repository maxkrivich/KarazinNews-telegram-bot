import os
import rssbot


def main():
    rss_list = [
        'http://www.univer.kharkov.ua/rss/anons.rss',
        'http://www.univer.kharkov.ua/rss/news.rss',
        'http://www.univer.kharkov.ua/rss/conf.rss',
        'http://landaucentre.org/feed/',
        'http://career.karazin.ua/feed/',
        'http://profkom.ua/feed/',
        # 'http://unk.kh.ua/feed/',
    ]
    sources = list(map(rssbot.RSSSource, rss_list))
    url_shortener = rssbot.BitlyShortifier(os.environ.get('BITLY_TOKEN'))
    bot = rssbot.RSSBot(
        token=os.environ.get('TELEGRAM_TOKEN'),
        shortener=url_shortener,
        channel_id=int(os.environ.get('TELEGRAM_CHAT_ID')),
        source_list=sources,
        db_uri=os.environ.get('DATABASE_URL')
    )

    bot.publish_news()


if __name__ == '__main__':
    main()
