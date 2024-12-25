from main import request_api, app, session
import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')
def request_api(script):
    print(script)
    try:
        url = os.getenv('API_URL')
        response = requests.post(url, json={'api_key': os.getenv('API_KEY'), 'script': script})
        return str(response.text), response.status_code
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    output, status = request_api('''
from .email_file import daily_report
daily_report()
    ''')
    print(f"output: {output}, status: {status}")