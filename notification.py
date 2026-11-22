import requests
import urllib3

from read_env import ReadEnv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Chat:

    def __init__(self):
        self.env: ReadEnv = ReadEnv()

    def send(self, contex: str) -> None:
        payload = {
            "channels":["chat"],
            "chatOptions": {
                "groupRecipients":[f"{self.env.chat_name}"]
            },
            "message":contex
        }
        try:
            response = requests.post(self.env.chat_url, json=payload, verify=False)
            if response.status_code == 200:
                print("Message send successfully!!!")
            else:
                print(f"Failed to send message. Status code: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"An error: {e}")