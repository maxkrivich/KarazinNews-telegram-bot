#! venv/bin/python3
# -*- coding: utf-8 -*-

import os
import configparser

config = configparser.ConfigParser()
config.read('./configs.ini')

DELAY_BETWEEN_MESSAGES = int(config['Export_params']['delay_between_messages'])

PUBLICATION_PAUSE = int(config['Export_params']['pub_pause'])

NEWS_RESOURCES = [config['RSS'][i] for i in config['RSS']]

TELEGRAM_CHAT_ID = -1001095757205

TELEGRAM_ACCESS_TOKEN = os.environ['TELEGRAM_ACCESS_TOKEN']

BITLY_ACCESS_TOKEN = os.environ['BITLY_ACCESS_TOKEN']

DATABASE_URL = os.environ['DATABASE_URL']

if __name__ == "__main__":
    print(DELAY_BETWEEN_MESSAGES)
    print(PUBLICATION_PAUSE)
    print(NEWS_RESOURCES)
    print(TELEGRAM_CHAT_ID)
    print(TELEGRAM_ACCESS_TOKEN)
    print(BITLY_ACCESS_TOKEN)
    print(DATABASE_URL)
