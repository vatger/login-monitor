import requests
from dotenv import load_dotenv
import os


load_dotenv()

path = os.getenv('DC_PATH')


def send_message(message: str):
    data = {
        'content': message,
        'username': 'Login monitor'
    }
    requests.post(path, data)
