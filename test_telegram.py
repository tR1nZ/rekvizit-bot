import requests

TOKEN = "8616395159:AAFQYgnyKXp7edldgPNeikmySbsEBdwhIoM"
url = f"https://api.telegram.org/bot{TOKEN}/getMe"

try:
    r = requests.get(url, timeout=20)
    print("STATUS:", r.status_code)
    print(r.text)
except Exception as e:
    print("ERROR:", repr(e))