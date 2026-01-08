import requests
try:
    r = requests.get('http://127.0.0.1:8000/api/groups/')
    print(r.status_code)
    for g in r.json():
        print(f"{g['name']} -> {g.get('slug')}")
except Exception as e:
    print(e)
