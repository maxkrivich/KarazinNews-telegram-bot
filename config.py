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

GOOGL_ACCESS_TOKEN = os.environ['GOOGL_ACCESS_TOKEN']

DATABASE_URL = os.environ['DATABASE_URL']


if __name__ == "__main__":
    print(DELAY_BETWEEN_MESSAGES)
    print(PUBLICATION_PAUSE)
    print(NEWS_RESOURCES)
    print(TELEGRAM_CHAT_ID)
    print(TELEGRAM_ACCESS_TOKEN)
    print(BITLY_ACCESS_TOKEN)
    print(GOOGL_ACCESS_TOKEN)
    print(DATABASE_URL)
