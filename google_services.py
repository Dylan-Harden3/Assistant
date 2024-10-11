from googleapiclient.discovery import build

from setup_credentials import setup_credentials


def get_gmail_service(creds=None):
    if creds is None:
        creds = setup_credentials()
    return build("gmail", "v1", credentials=creds)
