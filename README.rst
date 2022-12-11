=====
Python Telegram Logger
=====
Simple logger which dispatch messages to telegram in markdown format.
Uses a separate thread for a dispatching.
Support many chats.
Support big messages (over 4096 chars).
Support telegram API calls restrictions.


Installation
-----------
Install with::

    pip install git+https://github.com/charalamm/telegram-logger


Quick start
-----------
1. Crate a telegram bot and get the access token, aka `ACCESS_TOKEN_HTTP_API`

2. Through the telegram app create a group and put yourself and and the bot as members. Then get the chat group id, aka `GROUP_CHAT_ID`. The group chat id is one of the negative integers::

    import requests
    url = f"https://api.telegram.org/bot{ACCESS_TOKEN_HTTP_API}/getUpdates"
    print(requests.get(url).json())


3. Create a configuration file that defines the logger::

    import logging

    from python_telegram_logger import TelegramHandler, MarkdownFormatter

    # Logging
    logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)

    th = TelegramHandler(<ACCESS_TOKEN_HTTP_API>, [<GROUP_CHAT_ID>])
    th.setLevel(logging.ERROR)
    th.setFormatter(MarkdownFormatter())
    logger.addHandler(th)


4. Create another file that uses the logger::

    from configuration import logger

    def main():
    try:
    raise Exception("some exception")
    except Exception:
    logger.exception("catch!")

    main()
