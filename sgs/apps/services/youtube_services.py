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
        if not self._service:
            account = Account(config.client_secret_file, config.scopes)
            self._service = GoogleServices(account).youtube()
        return self._service


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
        items_list_request = self.service.playlistItems().list(
            playlistId=self.playlist_id,
            part='snippet',
            maxResults=5
        )
        while items_list_request:
            items_list_response = items_list_request.execute()
            # Save information about each uploaded video.
            for uploaded_video in items_list_response['items']:
                video = Video(self)
                video.item_id = uploaded_video['snippet']['resourceId']['videoId']
                video.title = uploaded_video['snippet']['title']
                video.description = uploaded_video['snippet']['description']
                video.published = uploaded_video['snippet']['publishedAt']
                self._my_videos.append(video)
            # Check if more videos are exists
            items_list_request = self.service.playlistItems().list_next(items_list_request, items_list_response)
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
        for video_comment_data in comments_response:
            comment_data = video_comment_data['snippet']['topLevelComment']['snippet']
            comment = Comment(self)
            comment.item_id = video_comment_data['snippet']['topLevelComment']['id']
            comment.published = comment_data['publishedAt']
            comment.updated = comment_data['updatedAt']
            comment.likes = comment_data['likeCount']
            comment.text = comment_data['textOriginal']
            comment.author = CommentAuthor(comment)
            comment.author.name = comment_data['authorDisplayName']
            comment.author.image_url = comment_data['authorProfileImageUrl']
            comment.author.channel_url = comment_data['authorChannelUrl']
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
    __slots__ = ('video', 'item_id', '_author', 'text', 'likes', 'published', 'updated', '_replies')

    def __init__(self, video: Video):
        super().__init__()
        self.video = video
        self.item_id: str = ''
        self._author = None
        self.text: str = ''
        self.likes: int = 0
        self.published: str = ''
        self.updated: str = ''
        self._replies: list = []

    def __str__(self):
        return self.text

    @property
    def replies(self) -> list:
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
            reply.text = reply_data['snippet']['textOriginal']
            reply.likes = reply_data['snippet']['likeCount']
            reply.published = reply_data['snippet']['publishedAt']
            reply.updated = reply_data['snippet']['updatedAt']
            reply.author = CommentAuthor(reply)
            reply.author.name = reply_data['snippet']['authorDisplayName']
            reply.author.image_url = reply_data['snippet']['authorProfileImageUrl']
            reply.author.channel_url = reply_data['snippet']['authorChannelUrl']
            self._replies.append(reply)
        return self._replies

    @property
    def replies_count(self) -> int:
        """
        Total number of replies for comment.
        """
        return len(self.replies)

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        self._author = author


class Reply(YoutubeService):
    """
    Subclass that contains data about reply for uploaded comment.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """

    __slots__ = ('comment', '_author', 'text', 'likes', 'published', 'updated')

    def __init__(self, comment: Comment):
        super().__init__()
        self.comment = comment
        self._author = None
        self.text: str = ''
        self.likes: int = 0
        self.published: str = ''
        self.updated: str = ''

    def __str__(self):
        return self.text

    @property
    def author(self):
        return self._author

    @author.setter
    def author(self, author):
        self._author = author


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
