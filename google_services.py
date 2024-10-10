import os.path
import pickle
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import os.path
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# source: https://developers.google.com/gmail/api/quickstart/python
def setup_credentials():
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send'
    ]
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=8080)
    with open("token.json", "w") as token:
      token.write(creds.to_json())
    
    return creds

def get_gmail_service(creds=None):
    if creds is None:
        creds = setup_credentials()
    return build('gmail', 'v1', credentials=creds)