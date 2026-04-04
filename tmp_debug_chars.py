import requests
import json

try:
    resp = requests.get("http://127.0.0.1:8000/api/v1/registry/tools")
    tools = resp.json()
    for t in tools:
        if "description" in t:
            desc = t["description"]
            print(f"Name: {t['name']}")
            print(f"Desc: {desc}")
            print(f"Chars: {[ord(c) for c in desc]}")
except Exception as e:
    print(f"Error: {e}")
