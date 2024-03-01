import requests
import json
import httpx

url = "http://127.0.0.1:2163/rag"

data = {
    "query_text": "Introduce me to te Mobox game?"
}

with requests.post(url, stream=True, json=data) as r:
    for chunk in r.iter_content(1024):
        chunk = chunk.decode('utf-8')
        print(chunk)
