__author__ = 'Yevhenii Dits'


from os import path

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class Account:

    def __init__(self, cred_path: str, scopes: list, token_json_path: str = None):
        self.cred_path = path.abspath(cred_path)
        if token_json_path is None:
            self.token_path = path.join(path.dirname(self.cred_path), 'token.json')
        else:
            self.token_path = token_json_path
        self.scopes = scopes


class GoogleServices:

    def __init__(self, account: Account):
        self.account = account

    def get_credentials(self):
        credentials = None
        # The file token.json stores the user's access and refresh tokens.
        # Created automatically when the authorization flow completes for the first time.
        if path.exists(self.account.token_path):
            credentials = Credentials.from_authorized_user_file(self.account.token_path, self.account.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.account.cred_path, self.account.scopes)
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.account.token_path, 'w') as token:
                token.write(credentials.to_json())
        return credentials

    def youtube(self):
        return build('youtube', 'v3', credentials=self.get_credentials(), cache_discovery=False)

    def drive(self):
        return build('drive', 'v3', credentials=self.get_credentials(), cache_discovery=False)
