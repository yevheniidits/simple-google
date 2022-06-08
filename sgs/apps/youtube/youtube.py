__author__ = 'Yevhenii Dits'


from sgs.apps.services import YoutubeService, Channel


class Youtube(YoutubeService):
    """
        Main class to work with Google API for Youtube.

        Available action sections:
            my_channel
    """
    def __init__(self):
        super().__init__()
        self._channel = None

    @property
    def _channel_response(self) -> dict:
        """
        API response as dictionary with full data about authenticated user`s channel.
        """
        return self.service.channels().list(mine=True, part='contentDetails').execute()['items']

    @property
    def my_channel(self):
        """
        Give access to methods and properties to get data about
        authenticated user`s channel, uploaded videos, comments etc.
        """
        if not self._channel:
            for item in self._channel_response:
                self._channel = Channel(item['id'])
                self._channel.playlist_id = item['contentDetails']['relatedPlaylists']['uploads']
                return self._channel
        return self._channel

    def like_video(self, video_id: str):
        self.service.videos().rate(id=video_id, rating='like').execute()

    def dislike_video(self, video_id: str):
        self.service.videos().rate(id=video_id, rating='dislike').execute()

