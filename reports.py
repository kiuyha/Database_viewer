from main import request_api, app, session
import os
import requests

api_key = 'gAAAAABnZ7M6e0K-mxXauaUUEY942lpLmTY01LU6JbE6YktBr0Jqo6wAjyTO1vfbfgr3jJRyNAf5JYHMaTRB1yuJeknWkSAOL-u2xBRpd70kGaGK6yys2niM8zrQf86S_5K8vehjGDcc'

def request_api(script):
    print(script)
    try:
        url = os.getenv('API_URL')
        response = requests.post(url, json={'api_key': api_key, 'script': script})
        return str(response.text), response.status_code
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    output, status = request_api('''
from .email_file import daily_report
daily_report()
    ''')
    print(f"output: {output}, status: {status}")