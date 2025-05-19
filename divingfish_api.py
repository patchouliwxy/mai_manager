import requests
import json

API_URL = "https://www.diving-fish.com/api/maimaidxprober/query/player"


def fetch_player_scores(import_token: str):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "token": import_token
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"请求失败：{response.status_code}, {response.text}")
