# KarazinNews RSS telegram bot
[![License](https://img.shields.io/badge/license-MIT%20license-green.svg?style=flat)]()
[![Telegram](https://img.shields.io/badge/telegram-channel-orange.svg?style=flat)](https://t.me/karazina)
[![Python](https://img.shields.io/badge/python-3.8-blue.svg?style=flat)]()
[![Requires.io](https://requires.io/github/maxkrivich/KarazinNews-telegram-bot/requirements.svg?branch=master&style=flat)](https://requires.io/github/maxkrivich/KarazinNews-telegram-bot/requirements/?branch=master)
[![Build Status](https://travis-ci.org/maxkrivich/KarazinNews-telegram-bot.svg?branch=master)](https://travis-ci.org/maxkrivich/KarazinNews-telegram-bot)


This is an unofficial Telegram-bot for [V.N. Karazin University](http://univer.kharkov.ua/en) which aggregates several useful sources for each student and professor of the uni. The main idea behind is quite simple to have all of the news in one [place](https://t.me/karazina).

![image](https://user-images.githubusercontent.com/12199867/101933467-87ac6c00-3bdc-11eb-97e9-9d2364435f98.png)


## Tech details
The bot is written in Python 3.8 and deployed into Heroku Cloud with Travis CI. In the current implementation, bot are using RSS-feed of various new sources.


### Local testing
If you are interested in contributing to the project you are very welcome! In this section, you can find commands which help you to setup the project on your local machine.

```bash
# step 0: Clone the repo
$ gh repo clone maxkrivich/KarazinNews-telegram-bot
$ cd KarazinNews-telegram-bot

# step 1: Setup virtualenv for the project
$ virtualenv --python=python3.8 .venv
$ source .venv/bin/activate
$ pip install -r requirements-dev.txt

# step 2: Specify environment variables
$ cp .env.example .env
$ vim .env

# step 3: DB setup
$ docker-compose -f docker-compose.dev.yaml up -d

# step 4: Launch script
$ python run.py

```

If you find [bugs] or have [suggestions] about improving the module, don't hesitate to contact me.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/maxkrivich/KarazinNews-telegram-bot/blob/master/LICENSE) file for details

Copyright (c) 2017-2020 - Maxim Krivich


[bugs]: <https://github.com/maxkrivich/KarazinNews-telegram-bot/issues>
[suggestions]: <https://github.com/maxkrivich/KarazinNews-telegram-bot/issues>
