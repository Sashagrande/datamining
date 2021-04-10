from pathlib import Path
import requests
import json

headers = {
    "User-Agent": "Alex"
}

url = "https://5ka.ru/api/v2/special_offers/"

response = requests.Response = requests.get(url, headers=headers)

file = Path(__file__).parent.joinpath('5ka.json')
file.write_text(response.text, encoding='utf-8')

data = json.loads(response.text)

print(1)