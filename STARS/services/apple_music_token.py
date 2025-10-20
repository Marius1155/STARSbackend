import jwt
import time
from decouple import config

# --- Config ---
KEY_ID = config('APPLE_MUSIC_KEY_ID')
TEAM_ID = config('APPLE_DEVELOPER_TEAM_ID')
PRIVATE_KEY = config('APPLE_MUSIC_PRIVATE_KEY').replace("\\n", "\n")  # read key from env
TOKEN_EXPIRATION = 15777000  # 6 months max in seconds (~183 days)

# --- Cache ---
_cached_token = None
_token_expiry = 0

def get_apple_music_token() -> str:
    """Returns a valid Apple Music developer token, auto-generating if expired or missing."""
    global _cached_token, _token_expiry
    now = int(time.time())
    if _cached_token is None or now >= _token_expiry - 60:  # regenerate 1 min before expiry
        payload = {
            "iss": TEAM_ID,
            "iat": now,
            "exp": now + TOKEN_EXPIRATION
        }
        headers = {"alg": "ES256", "kid": KEY_ID}
        _cached_token = jwt.encode(payload, PRIVATE_KEY, algorithm="ES256", headers=headers)
        _token_expiry = now + TOKEN_EXPIRATION
    return _cached_token