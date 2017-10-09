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
import botan
import config
import telebot
import messages

from flask import Flask, request

bot = telebot.TeleBot(config.TELEGRAM_ACCESS_TOKEN)

server = Flask(__name__)

"""
Commands:
/start - Початок роботи з ботом [+]
/help - Отримати коротку довiдку [-]
/add_news_source - Додати нове джерело [-]
/get_latest_news - Отримати останнi новини [-]
"""

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, messages.START_MESSAGE.format(
        name=message.from_user.first_name), parse_mode="HTML")
    botan.track(message.chat.id, message, 'start')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, messages.UNKNOWN_ACTION)
    botan.track(message.chat.id, message, 'unknown_action')

@server.route("/" + config.TELEGRAM_ACCESS_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=config.HEROKU_URL + config.TELEGRAM_ACCESS_TOKEN)
    return "!", 200
