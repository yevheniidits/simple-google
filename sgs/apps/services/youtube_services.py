__author__ = 'Yevhenii Dits'


from typing import Union
from datetime import datetime

from googleapiclient.errors import HttpError

from sgs.apps.services.google_account import Account, GoogleServices
from sgs import config


class YoutubeService:

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

    @staticmethod
    def _string_to_datetime(date_string: str, date_format: str = '%Y-%m-%dT%H:%M:%SZ'):
        return datetime.strptime(date_string, date_format)


class Channel(YoutubeService):
    """
    Subclass that contains data about authenticated user`s channel.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """
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
        self._my_videos = []
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

    @property
    def statistic(self) -> dict:
        results = self.service.channels().list(
            part='snippet,contentDetails,statistics',
            id=self.item_id
        ).execute()
        return {
            'id': results['items'][0]['id'],
            'title': results['items'][0]['snippet']['title'],
            'views': results['items'][0]['statistics']['viewCount']
        }

    def get_video_by_id(self, video_id: str) -> 'Video':
        for video in self.my_videos:
            if video.item_id == video_id:
                return video

    def get_videos_by_title(self, title: str, contains: bool = False) -> list:
        my_videos = self.my_videos
        exact_match = [video for video in my_videos if video.title == title]
        if contains:
            partial_match = [video for video in my_videos if title in video.title]
            exact_match.extend(partial_match)
            exact_match = list(set(exact_match))
        return exact_match


class Video(YoutubeService):
    """
    Subclass that contains data about authenticated user`s uploaded video.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """
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

    @property
    def published_as_datetime(self) -> datetime:
        return self._string_to_datetime(self.published)

    @property
    def published_as_string(self) -> str:
        return self.published

    def find_comment_by_id(self, item_id: str) -> 'Comment':
        for comment in self.comments:
            if comment.item_id == item_id:
                return comment

    def get_comment_by_author(self, author_name: str) -> list:
        return [comment for comment in self.comments if comment.author.name == author_name]

    def get_comments_by_text(self, text: str) -> list:
        return [comment for comment in self.comments if text in comment.text]

    def get_messages_by_author(self, author_name: str) -> list:
        messages = []
        for comment in self.comments:
            if comment.author.name == author_name:
                messages.append(comment)
            for reply in comment.replies:
                if reply.author.name == author_name:
                    messages.append(reply)
        return messages

    def update_video(
            self,
            title: str = None,
            description: str = None,
            new_tags: list = None,
            add_tag: str = None
    ):
        videos_list_response = self.service.videos().list(
            id=self.item_id,
            part='snippet'
        ).execute()
        if not videos_list_response['items']:
            raise Exception(f'Video with id {self.item_id} not found')
        videos_list_snippet = videos_list_response['items'][0]['snippet']
        if title:
            videos_list_snippet['title'] = title
        if description:
            videos_list_snippet['description'] = description
        if 'tags' not in videos_list_snippet:
            videos_list_snippet['tags'] = []
        if new_tags:
            videos_list_snippet['tags'] = new_tags
        elif add_tag:
            videos_list_snippet['tags'].append(add_tag)
        self.service.videos().update(
            part='snippet',
            body=dict(
                snippet=videos_list_snippet,
                id=self.item_id
            )
        ).execute()
        return self.channel.get_video_by_id(self.item_id)


class Message(YoutubeService):
    """
    Base class with common methods for both comment and reply message types.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """
    def __init__(self):
        super().__init__()
        self.item_id = None
        self.author = None
        self.text = None
        self.likes = None
        self.published = None
        self.updated = None

    def __str__(self):
        return self.text

    @property
    def published_as_datetime(self) -> datetime:
        return self._string_to_datetime(self.published)

    @property
    def published_as_string(self) -> str:
        return self.published

    @property
    def updated_as_datetime(self) -> datetime:
        return self._string_to_datetime(self.updated)

    @property
    def updated_as_string(self) -> str:
        return self.updated

    def delete_own_message(self):
        """
        Delete selected message.
        :return: deleted message id
        """
        try:
            self.service.comments().delete(id=self.item_id).execute()
        except HttpError:
            raise Exception('Can`t delete message. You are not message owner.')
        return self.item_id

    def mark_as_spam(self) -> str:
        """
        Mark selected comment as spam
        :return: comment id
        """
        self.service.comments().markAsSpam(id=self.item_id).execute()
        return self.item_id


class Comment(Message):
    """
    Subclass that contains data about comment for uploaded video.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """
    def __init__(self, video: Video):
        super().__init__()
        self.video = video
        self._replies = []

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
        :return: total number of replies for comment.
        """
        return len(self.replies)

    def add_reply(self, text: str) -> 'Reply':
        """
        Add reply for selected comment.
        :param text: reply text
        :return: new Reply object
        """
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

    def get_reply_by_id(self, item_id: str) -> 'Reply':
        for reply in self.replies:
            if reply.item_id == item_id:
                return reply

    def get_replies_by_author(self, author_name: str) -> list:
        return [reply for reply in self.replies if reply.author.name == author_name]

    def get_replies_by_text(self, text: str) -> list:
        return [reply for reply in self.replies if text in reply.text]


class Reply(Message):
    """
    Subclass that contains data about reply for uploaded comment.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """
    def __init__(self, comment: Comment):
        super().__init__()
        self.comment = comment

    def add_reply(self, text: str) -> 'Reply':
        """
        Add reply for selected reply.
        :param text: reply text
        :return: new Reply object
        """
        reply_data = self.service.comments().insert(
            part="snippet",
            body=dict(
                snippet=dict(
                    parentId=self.comment.item_id,
                    textOriginal=text
                )
            )
        ).execute()
        reply = Reply(self.comment)
        self._save_comment(reply, reply_data)
        return reply


class CommentAuthor(YoutubeService):
    """
    Subclass that contains data about comment/reply author.
    NOT FOR DIRECT USING. Use Youtube class instead.
    """
    def __init__(self, comment: Union[Comment, Reply]):
        super().__init__()
        self.comment = comment
        self.name = None
        self.image_url = None
        self.channel_url = None

    def __str__(self):
        return self.name
