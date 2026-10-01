import pytz

import datetime
import logging
import time

# noinspection PyUnresolvedReferences
from telethon import TelegramClient, events, sync

import alert_parser
import config
from alert_parser import Alert
from db_worker import DBWorker
from tg_bot import TGBot

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger('alert_checker')

POLL_INTERVAL = 60
MESSAGES_PER_POLL = 5


def normalize_status(raw):
    """Maps values stored in the DB (including the legacy ones) to statuses."""
    if raw == config.ALERT_ON:
        return alert_parser.ON
    if raw == config.ALERT_OFF:
        return alert_parser.OFF
    return raw


def last_status():
    with DBWorker() as w:
        return normalize_status(w.get_status())


def save_status(new_status):
    with DBWorker() as w:
        w.insert_status(new_status)


def local_time():
    local = pytz.timezone('Europe/Kyiv').fromutc(datetime.datetime.utcnow())
    return datetime.datetime.strftime(local, "%H:%M:%S %d-%m-%Y")


def alert_text(alert: Alert):
    if alert.status == alert_parser.YELLOW:
        text = '\U0001F7E1 Повітряна тривога, жовтий рівень'
    elif alert.status == alert_parser.RED:
        text = '\U0001F534 Повітряна тривога, червоний рівень'
    elif alert.status == alert_parser.ON:
        text = '\U0001F534 Повітряна тривога!'
    else:
        text = '\U0001F7E2 Відбій повітряної тривоги'
    if alert.threat:
        text += f': {alert.threat}'
    return f'{text}\n{local_time()}'


def notify_if_changed(alert: Alert):
    if last_status() == alert.status:
        return
    TGBot(alert_text(alert))
    save_status(alert.status)


def parse_legacy(text):
    return alert_parser.parse_legacy(
        text, config.ALERT_ON, config.ALERT_OFF)


def parse_new(text):
    return alert_parser.parse_new(text, config.NEW_SOURCE_AREA)


class Source:
    """Polls a channel and yields alerts from messages not seen yet."""

    def __init__(self, client, channel, parse):
        self.client = client
        self.channel = channel
        self.parse = parse
        self.last_id = None

    def new_alerts(self):
        messages = self.client.get_messages(
            self.channel, limit=MESSAGES_PER_POLL)
        messages = sorted(
            (m for m in messages if m.message), key=lambda m: m.id)
        if self.last_id is None:
            # first poll after start: only the actual state matters, replaying
            # history would spam; the DB check dedups an unchanged state
            parsed = [(m, self.parse(m.message)) for m in messages]
            parsed = [(m, a) for m, a in parsed if a]
            if messages:
                self.last_id = messages[-1].id
            return [a for _, a in parsed[-1:]]
        alerts = []
        for m in messages:
            if m.id <= self.last_id:
                continue
            self.last_id = m.id
            alert = self.parse(m.message)
            if alert:
                alerts.append(alert)
        return alerts


def build_sources(client):
    mode = config.ALERT_SOURCE_MODE
    legacy = Source(client, config.SOURCE_CHANNEL_NAME, parse_legacy)
    new = Source(client, config.NEW_SOURCE_CHANNEL_NAME, parse_new)
    if mode == 'legacy':
        return [legacy], []
    if mode == 'shadow':
        return [legacy], [new]
    if mode == 'new':
        return [new], []
    raise ValueError(f'Unknown ALERT_SOURCE_MODE: {mode}')


def poll(source, shadow=False):
    try:
        alerts = source.new_alerts()
    except Exception:
        log.exception('Failed to read %s', source.channel)
        return
    for alert in alerts:
        if shadow:
            log.info('[shadow] %s would send: %s', source.channel,
                     alert_text(alert).replace('\n', ' | '))
            continue
        try:
            notify_if_changed(alert)
        except Exception:
            log.exception('Failed to process alert %s', alert)


def check_alert_status():
    client = TelegramClient('electricity_status_bot',
                            config.TG_API_ID, config.TG_API_HASH)
    client.start()
    sources, shadow_sources = build_sources(client)
    log.info('Started, mode=%s', config.ALERT_SOURCE_MODE)

    while True:
        for source in sources:
            poll(source)
        for source in shadow_sources:
            poll(source, shadow=True)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    check_alert_status()
