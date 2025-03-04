import logging.handlers
import requests
import time

from queue import Queue


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class TelegramHandler(logging.handlers.QueueHandler):
    """
    Separate thread for a message dispatching
    """
    TIMEOUT = 13  # seconds
    MAX_MSG_LEN = 4096
    API_CALL_INTERVAL = 1 / 30  # 30 calls per second
    START_CODE_BLOCK = END_CODE_BLOCK = "```"
    MODE = "MarkdownV2"

    def __init__(self, token: str, chat_ids: list, disable_notifications: bool=False, disable_preview: bool=False):
        """
        See Handler args
        """
        self.token = token
        self.chat_ids = [int(chat_id) for chat_id in chat_ids]
        self.disable_notifications = disable_notifications
        self.disable_preview = disable_preview
        self.session = requests.Session()

        queue = Queue()
        super().__init__(queue)

    @property
    def url(self):
        return "https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={text}&parse_mode={mode}"

    def handle(self, record):
        """
        Perform message splitting in case if it is big
        """
        record = self.format(record)

        if len(record) > self.MAX_MSG_LEN:

            # telegram max length of text is 4096 chars, we need to split our text into chunks

            start_idx, end_idx = 0, self.MAX_MSG_LEN - len(self.END_CODE_BLOCK)
            new_record = record[start_idx:end_idx]

            while new_record:
                # remove whitespaces, markdown fmt symbols and a carriage return
                new_record = self.START_CODE_BLOCK + new_record + self.END_CODE_BLOCK
                self.emit(new_record)

                start_idx, end_idx = end_idx, end_idx + self.MAX_MSG_LEN - (len(self.START_CODE_BLOCK) + len(self.END_CODE_BLOCK))
                new_record = record[start_idx:end_idx]
        else:
            self.emit(self.START_CODE_BLOCK + record + self.END_CODE_BLOCK)

    def emit(self, record):
        for chat_id in self.chat_ids:
            url = self.url.format(
                token=self.token,
                chat_id=chat_id,
                mode=self.MODE,
                text=record,
                disable_web_page_preview=self.disable_preview,
                disable_notifications=self.disable_notifications
            )

            response = self.session.get(url, timeout=self.TIMEOUT)
            if not response.ok:
                logger.warning("Telegram log dispatching failed with status code '%s'" % response.status_code)
                logger.warning("Response is: %s" % response.text)

            # telegram API restrict more than 30 calls per second, this is a very pessimistic sleep,
            # but should work as a temporary workaround
            time.sleep(self.API_CALL_INTERVAL)

    def __del__(self):
        self.session.close()
