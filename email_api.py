import requests
from dotenv import load_dotenv
import os

load_dotenv()
auth = (os.getenv('EMAIL_API_KEY_PUBLIC'), os.getenv('EMAIL_API_KEY_PRIVATE'))

def kirim_konfimasi_email(email:str, name:str, otp:str):
    
    url = 'https://api.mailjet.com/v3.1/send'

    headers = {
        'Content-Type': 'application/json'
    }

    body = {
        "Messages": [
            {
                "From": {
                    "Email": "swift.e_learning@hotmail.com",
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
                "Subject": "Konfirmasi Email Swift E-Learning",
                "Variables": {
                    "name": name,
                    "otp": otp
                }
            }
        ]
    }

    response = requests.post(url, json=body, headers=headers, auth=auth)

    print(auth)
    print(response.status_code)
    print(response.json())

