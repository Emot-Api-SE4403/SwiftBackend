import requests
from dotenv import load_dotenv
import os

load_dotenv()
auth = (os.getenv('EMAIL_API_KEY_PUBLIC'), os.getenv('EMAIL_API_KEY_PRIVATE'))
my_email = os.getenv('MY_EMAIL')

def kirim_konfimasi_email(email:str, name:str, otp:str):
    
    url = 'https://api.mailjet.com/v3.1/send'

    headers = {
        'Content-Type': 'application/json'
    }

    body = {
        "Messages": [
            {
                "From": {
                    "Email": my_email,
                    "Name": "noreply-Swfit E-Learning"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": name
                    }
                ],
                "TemplateID": 4647702,
                "TemplateLanguage": True,
                "Subject": "Konfirmasi email Swift E-Learning",
                "Variables": {
                    "field1": otp
                }
            }
        ]
    }

    response = requests.post(url, json=body, headers=headers, auth=auth)

def kirim_password_baru(email:str, name:str, password:str):
    
    url = 'https://api.mailjet.com/v3.1/send'

    headers = {
        'Content-Type': 'application/json'
    }

    body = {
        "Messages": [
            {
                "From": {
                    "Email": my_email,
                    "Name": "noreply-Swfit E-Learning"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": name
                    }
                ],
                "TemplateID": 4647704,
                "TemplateLanguage": True,
                "Subject": "Reset password Swift E-Learning",
                "Variables": {
                    "name": name,
                    "otp": password
                }
            }
        ]
    }

    response = requests.post(url, json=body, headers=headers, auth=auth)


