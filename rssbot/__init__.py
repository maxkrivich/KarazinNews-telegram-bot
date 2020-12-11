import logging
import os


from .db import Database, News  # isort:skip
from .rss_source import RSSSource  # isort:skip
from .url_shortener import BitlyShortifier, GooglShortifier, URLShortifier  # isort:skip
from .bot import RSSBot  # isort:skip

if os.environ.get('APP_ENV') in ('staging', 'develop'):
    lvl = logging.DEBUG
elif os.environ.get('APP_ENV') == 'production':
    lvl = logging.INFO

logging.basicConfig(
    level=lvl, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
