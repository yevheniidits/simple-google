__author__ = 'Yevhenii Dits'


from sgs.apps.services import YoutubeService, Channel


class Youtube(YoutubeService):
    """
        Main class to work with Google API for Youtube.

        Available action sections:
            my_channel
    """
    __slots__ = ('_channel_response', '_channel')

    def __init__(self):
        super().__init__()
        self._channel_response = None
        self._channel = None

    @property
    def channel_response(self) -> dict:
        """
        API response as dictionary with full data about authenticated user`s channel.
        """
        if not self._channel_response:
            self._channel_response = self.service.channels().list(mine=True, part='contentDetails').execute()['items']
        return self._channel_response

    @property
    def my_channel(self):
        """
        Give access to methods and properties to get data about
        authenticated user`s channel, uploaded videos, comments etc.
        """
        if not self._channel:
            for item in self.channel_response:
                self._channel = Channel(item['id'])
                self._channel.playlist_id = item['contentDetails']['relatedPlaylists']['uploads']
                return self._channel
        return self._channel
