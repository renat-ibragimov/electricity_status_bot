import requests

import config


class TGBot:
    def __init__(self, message: str):
        self.message = message
        self.send_msg()

    def send_msg(self):
        chat_ids = [
            config.PRIMORSKII_COURT_CHANNEL_ID,
            config.HADJIBEYSKII_COURT_CHANNEL_ID,
        ]
        for chat_id in chat_ids:
            requests.post(
                f"https://api.telegram.org/bot{config.PRIMORSKII_COURT_BOT_TOKEN}/sendMessage",
                data={"chat_id": chat_id, "text": self.message}
            )
