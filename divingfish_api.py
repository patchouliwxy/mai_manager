# divingfish_api.py
import requests
import json

API_URL = "https://www.diving-fish.com/api/maimaidxprober/player/records"
LOGIN_URL = "https://www.diving-fish.com/api/maimaidxprober/login"


def login(username: str, password: str, session: requests.Session) -> str:
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "username": username,
        "password": password
    }

    response = session.post(LOGIN_URL, json=payload, headers=headers)

    if response.status_code == 200:
        jwt_token = response.cookies.get("jwt_token", "")
        if not jwt_token:
            raise Exception("登录失败：未收到 jwt_token")
        return jwt_token
    else:
        try:
            error_message = response.json().get("message", response.text)
        except:
            error_message = response.text
        raise Exception(f"登录失败：{response.status_code}, {error_message}")


def fetch_player_scores(session: requests.Session):
    response = session.get(API_URL)

    if response.status_code == 200:
        return response.json()
    else:
        try:
            error_message = response.json().get("message", response.text)
        except:
            error_message = response.text
        if response.status_code == 403:
            error_message = "无法获取成绩：请在 https://www.diving-fish.com/maimaidx/prober/ 检查是否同意用户协议或关闭隐私保护设置。"
        raise Exception(f"请求失败：{response.status_code}, {error_message}")