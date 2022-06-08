__author__ = 'Yevhenii Dits'


import json
from os import environ
from os.path import join, expanduser, exists


class Config:

    def __init__(self):
        self._config_file = None
        self._config_dict = None
        self._local_config_file = join(expanduser('~'), '.sgs', 'config.json')
        self._env_config_key = 'SGS_CONFIGFILE'

        self._client_secret_file = None
        self._local_client_secret_file = join(expanduser('~'), '.sgs', 'client_secret.json')
        self._env_client_secret_key = 'SGS_CLIENTSECRET'

        self._scopes = {}
        self._project_scopes = []

    @property
    def config_file(self):
        if not self._config_file:
            self._config_file = environ.get(self._env_config_key) or self._local_config_file
            if not exists(self._config_file):
                raise FileNotFoundError(
                    """Can`t load config file."""
                    """\nPlease do one of the following:"""
                    f"""\n1. Set path to file as env variable '{self._env_config_key}'"""
                    f"""\n2. Place file at {self._local_config_file}"""
                    """\n3. Set custom path to file"""
                    """\n\tfrom sgs import config"""
                    """\n\tconfig.config_file = 'path to config.json file'"""
                    """\n4. Set config manually"""
                    """\n\tfrom sgs import config"""
                    """\n\tconfig.config_dict = {"key": "value", ...}"""
                )
        return self._config_file

    @config_file.setter
    def config_file(self, path: str):
        self._config_file = path

    @property
    def config_dict(self):
        if not self._config_dict:
            with open(self.config_file) as file:
                self._config_dict = json.load(file)
        return self._config_dict

    @config_dict.setter
    def config_dict(self, config):
        self._config_dict = config

    @property
    def client_secret_file(self):
        if not self._client_secret_file:
            self._client_secret_file = environ.get(self._env_client_secret_key) or self._local_client_secret_file
        if not exists(self._client_secret_file):
            raise FileNotFoundError(
                """Can`t find client secret json file."""
                """\nPlease do one of the following:"""
                f"""\n1. Set path to file as env variable {self._env_client_secret_key}"""
                f"""\n2. Place file at {self._local_client_secret_file}""" 
                """\n3. Set custom path to file""" 
                """\n\tfrom sgs import config""" 
                """\n\tconfig.client_secret_file = 'path to client_secret.json file'"""
                """\nFor instructions how to create project in Google Cloud Platform"""
                """\nand get credentials file please visit"""
                """\n\thttps://developers.google.com/workspace/guides/create-project"""
                """\n\thttps://developers.google.com/workspace/guides/create-credentials"""
            )
        return self._client_secret_file

    @client_secret_file.setter
    def client_secret_file(self, path: str):
        self._client_secret_file = path

    @property
    def scopes(self):
        if not self._scopes:
            config_file_scopes = self.config_dict.get('scopes', {})
            if not config_file_scopes:
                raise Exception(
                    """Can`t read scopes from config."""
                    """\nPlease do one of the following"""
                    """\n(replace "service" with service name e.g. "youtube", "drive" etc.):"""
                    """\n1. Scopes config structure must be {"scopes": {"service": ["scope_1", "scope_2", ...]}, ...}"""
                    """\n2. Set scopes manually"""
                    """\n\tfrom sgs import config"""
                    """\n\tconfig.scopes["service"] = ["scope_1", "scope_2", ...]"""
                )
            for service, scopes in config_file_scopes.items():
                self._scopes[service] = scopes
                self._scopes[service] = list(set(self._scopes[service]))
        return self._scopes

    @scopes.setter
    def scopes(self, scopes: dict):
        for service, scope in scopes.items():
            if not isinstance(scope, list):
                raise TypeError('Scopes must be list of strings')
        self._scopes = scopes

    @property
    def project_scopes(self):
        self._project_scopes = list(set(self._project_scopes))
        return self._project_scopes

    @project_scopes.setter
    def project_scopes(self, scopes: list):
        self._project_scopes.extend(scopes)

    @project_scopes.deleter
    def project_scopes(self):
        self._project_scopes = []

    get = config_dict
