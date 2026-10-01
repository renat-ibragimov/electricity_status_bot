import os

from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_LOCAL_PORT = os.getenv('DB_LOCAL_PORT')

TG_API_ID = os.getenv('TG_API_ID')
TG_API_HASH = os.getenv('TG_API_HASH')

PRIMORSKII_COURT_BOT_TOKEN = os.getenv('PRIMORSKII_COURT_BOT_TOKEN')
PRIMORSKII_COURT_CHANNEL_ID = os.getenv('PRIMORSKII_COURT_CHANNEL_ID')
HADJIBEYSKII_COURT_CHANNEL_ID = os.getenv('HADJIBEYSKII_COURT_CHANNEL_ID')

SOURCE_CHANNEL_NAME = os.getenv('SOURCE_CHANNEL_NAME')

# Migration to the new source channel (yellow/red alerts):
#   legacy - only SOURCE_CHANNEL_NAME drives notifications (default)
#   shadow - SOURCE_CHANNEL_NAME drives notifications, NEW_SOURCE_CHANNEL_NAME
#            is only parsed and logged for comparison
#   new    - only NEW_SOURCE_CHANNEL_NAME drives notifications
ALERT_SOURCE_MODE = os.getenv('ALERT_SOURCE_MODE', 'legacy')
NEW_SOURCE_CHANNEL_NAME = os.getenv('NEW_SOURCE_CHANNEL_NAME')
NEW_SOURCE_AREA = os.getenv('NEW_SOURCE_AREA', 'Одеський район')

ALERT_ON = os.getenv('ALERT_ON')
ALERT_OFF = os.getenv('ALERT_OFF')
