import logging
import re
from typing import NamedTuple, Optional

OFF = 'off'
ON = 'on'  # legacy source: alert without a level
YELLOW = 'yellow'
RED = 'red'

log = logging.getLogger(__name__)

MAX_ALERT_LENGTH = 300
_THREAT_RE = re.compile(r':\s*([^()\n]+?)\s*(?:\(|$)')


class Alert(NamedTuple):
    status: str
    threat: Optional[str] = None


def parse_legacy(text: str, alert_on: str, alert_off: str) -> Optional[Alert]:
    """Old source: the status is the last word of the message."""
    words = text.split()
    if not words:
        return None
    if words[-1] == alert_on:
        return Alert(ON)
    if words[-1] == alert_off:
        return Alert(OFF)
    return None


def parse_new(text: str, area: str = '') -> Optional[Alert]:
    """New source, e.g. 'Одеський район — повітряна тривога, жовтий рівень:
    Дронова загроза (жовтий рівень)' or '... відбій повітряної тривоги'.

    The channel also posts news, so a message is treated as an alert only
    when it is short and starts with the area name. Inside such a message the
    parsing is keyword (word stem) based on purpose: when the wording changes
    we would rather send a generic alert than miss one."""
    if not text:
        return None
    text = text.strip()
    lowered = text.lower()
    if len(text) > MAX_ALERT_LENGTH:
        return None
    if area and not re.match(r'[\W_]*' + re.escape(area), text, re.IGNORECASE):
        if 'тривог' in lowered or 'відбій' in lowered:
            log.warning('Not an alert for %s, ignored: %s', area, text)
        return None
    if 'відбій' in lowered:
        return Alert(OFF)
    if 'тривог' not in lowered:
        return None
    threat = _THREAT_RE.search(text)
    threat = threat.group(1) if threat else None
    if 'червон' in lowered:
        return Alert(RED, threat)
    if 'жовт' in lowered:
        return Alert(YELLOW, threat)
    return Alert(ON, threat)
