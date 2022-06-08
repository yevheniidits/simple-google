__author__ = 'Yevhenii Dits'


from sgs.apps.services.google_account import Account, GoogleServices
from sgs import config


class DriveService:

    def __init__(self):
        config.project_scopes = config.scopes['drive']
        self._service = None

    @property
    def service(self):
        """
        Create Resource object for interacting with Youtube API
        """
        if not self._service:
            account = Account(config.client_secret_file, config.project_scopes)
            self._service = GoogleServices(account).drive()
        return self._service

    @staticmethod
    def _save_file(file: 'File', api_response: dict):
        file.item_id = api_response['id']
        file.name = api_response['name']
        file.type = api_response['mimeType']
        return


class Storage(DriveService):

    def __init__(self):
        super().__init__()
        self._files = []

    @property
    def files(self):
        full_api_response = self.service.files().list().execute()
        for api_response in full_api_response['files']:
            file = File(self)
            self._save_file(file, api_response)
            self._files.append(file)
        return self._files


class File(DriveService):

    def __init__(self, storage: 'Storage'):
        super().__init__()
        self.storage = storage
        self.item_id = None
        self.name = None
        self.type = None
