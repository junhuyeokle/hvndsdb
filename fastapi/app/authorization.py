import hashlib
import hmac
import time

from envs import WS_KEY

TIMESTAMP_VALID_WINDOW = 3  # seconds


def is_valid_timestamp(ts: str) -> bool:
    try:
        now = int(time.time())
        ts_int = int(ts)
        return abs(now - ts_int) <= TIMESTAMP_VALID_WINDOW
    except ValueError:
        return False


def verify_hmac(ts: str, sig: str) -> bool:
    expected = hmac.new(
        WS_KEY.encode(), ts.encode(), hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, sig)
