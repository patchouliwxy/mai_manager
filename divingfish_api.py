import requests
import json

API_URL = "https://www.diving-fish.com/api/maimaidxprober/player/records"

def fetch_player_scores(import_token: str):
    headers = {
        "Content-Type": "application/json",
        "Import-Token": import_token  # 将 Import-Token 放入 headers
    }

    response = requests.get(API_URL, headers=headers)  # 使用 GET 请求

    if response.status_code == 200:
        return response.json()
    else:
        try:
            error_message = response.json().get("message", response.text)
        except:
            error_message = response.text
        raise Exception(f"请求失败：{response.status_code}, {error_message}")