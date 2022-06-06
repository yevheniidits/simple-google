__author__ = 'Yevhenii Dits'


from typing import Union

from sgs.apps.services.google_account import Account, GoogleServices
from sgs import config


class YoutubeService:

    __slots__ = ('_service',)

    def __init__(self):
        self._service = None

    @property
    def service(self):
        """
        Create Resource object for interacting with Youtube API
        """
        if not self._service:
            account = Account(config.client_secret_file, config.scopes)
            self._service = GoogleServices(account).youtube()
        return self._service

    @staticmethod
    def _save_comment(comment: Union['Comment', 'Reply'], api_response: dict):
        """
        Parse API data and update selected Comment/Reply and CommentAuthor instances.
        :param comment: Comment or Reply instance
        :param api_response: response from API
        """
        if api_response['kind'] == 'youtube#commentThread':
            api_response = api_response['snippet']['topLevelComment']
        comment.item_id = api_response['id']
        comment.text = api_response['snippet']['textOriginal']
        comment.likes = api_response['snippet']['likeCount']
        comment.published = api_response['snippet']['publishedAt']
        comment.updated = api_response['snippet']['updatedAt']
        comment.author = CommentAuthor(comment)
        comment.author.name = api_response['snippet']['authorDisplayName']
        comment.author.image_url = api_response['snippet']['authorProfileImageUrl']
        comment.author.channel_url = api_response['snippet']['authorChannelUrl']
        return

    @staticmethod
    def _save_video(video: 'Video', api_response: dict):
        """
        Parse API data and update selected Video instance.
        :param video: Video instance
        :param api_response: response from API
        """
        video.item_id = api_response['snippet']['resourceId']['videoId']
        video.title = api_response['snippet']['title']
        video.description = api_response['snippet']['description']
        video.published = api_response['snippet']['publishedAt']
        return


class Channel(YoutubeService):
    """
    Subclass that contains data about authenticated user`s channel.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """

    __slots__ = ('item_id', 'playlist_id', '_my_videos')

    def __init__(self, channel_id: str):
        super().__init__()
        self.item_id = channel_id
        self.playlist_id = None
        self._my_videos = []

    def __str__(self):
        return self.item_id

    @property
    def my_videos(self) -> list:
        """
        Retrieve the list of videos uploaded to the authenticated user's channel.
        """
        api_request = self.service.playlistItems().list(
            playlistId=self.playlist_id,
            part='snippet',
            maxResults=5
        )
        while api_request:
            api_response = api_request.execute()
            # Save information about each uploaded video.
            for video_api_response in api_response['items']:
                video = Video(self)
                self._save_video(video, video_api_response)
                self._my_videos.append(video)
            # Check if more videos are exists
            api_request = self.service.playlistItems().list_next(api_request, api_response)
        return self._my_videos

    @property
    def videos_count(self) -> int:
        """
        Total number of videos on authenticated user`s channel.
        """
        return len(self.my_videos)


class Video(YoutubeService):
    """
    Subclass that contains data about authenticated user`s uploaded video.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """

    __slots__ = ('channel', 'item_id', 'title', 'description', 'published', '_comments')

    def __init__(self, channel: Channel):
        super().__init__()
        self.channel = channel
        self.item_id = None
        self.title = None
        self.description = None
        self.published = None
        self._comments = []

    def __str__(self):
        return self.title

    @property
    def comments(self) -> list:
        """
        Retrieve the list of comments for uploaded video.
        """
        comments_response = self.service.commentThreads().list(
            part='snippet',
            videoId=self.item_id,
            textFormat='plainText'
        ).execute()['items']
        for response_data in comments_response:
            comment = Comment(self)
            self._save_comment(comment, response_data)
            self._comments.append(comment)
        return self._comments

    @property
    def comments_count(self) -> int:
        """
        Total number of comments for video.
        """
        return len(self.comments)


class Comment(YoutubeService):
    """
    Subclass that contains data about comment for uploaded video.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """

    __slots__ = ('video', 'item_id', 'author', 'text', 'likes', 'published', 'updated', '_replies')

    def __init__(self, video: Video):
        super().__init__()
        self.video = video
        self.item_id = None
        self.author = None
        self.text = None
        self.likes = None
        self.published = None
        self.updated = None
        self._replies = []

    def __str__(self):
        return self.text

    @property
    def replies(self):
        """
        Retrieve the list of replies for comment.
        """
        replies_response = self.service.comments().list(
            part='snippet',
            parentId=self.item_id,
            textFormat='plainText'
        ).execute()['items']
        for reply_data in replies_response:
            reply = Reply(self)
            self._save_comment(reply, reply_data)
            self._replies.append(reply)
        return self._replies

    @property
    def replies_count(self):
        """
        Total number of replies for comment.
        """
        return len(self.replies)

    def add_reply(self, text: str):
        reply_data = self.service.comments().insert(
            part="snippet",
            body=dict(
                snippet=dict(
                    parentId=self.item_id,
                    textOriginal=text
                )
            )
        ).execute()
        reply = Reply(self)
        self._save_comment(reply, reply_data)
        return reply


class Reply(YoutubeService):
    """
    Subclass that contains data about reply for uploaded comment.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """

    __slots__ = ('comment', 'item_id', 'author', 'text', 'likes', 'published', 'updated')

    def __init__(self, comment: Comment):
        super().__init__()
        self.comment = comment
        self.item_id = None
        self.author = None
        self.text = None
        self.likes = None
        self.published = None
        self.updated = None

    def __str__(self):
        return self.text


class CommentAuthor(YoutubeService):
    """
    Subclass that contains data about comment/reply author.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """

    __slots__ = ('comment', 'name', 'image_url', 'channel_url')

    def __init__(self, comment: Union[Comment, Reply]):
        super().__init__()
        self.comment = comment
        self.name = None
        self.image_url = None
        self.channel_url = None

    def __str__(self):
        return self.name
