# sgs (Simple Google Services)

Simplifies interaction with Google API for most frequently used tasks. Based on google-api-python-client.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install sgs.

```bash
pip install git+https://git@github.com/yevheniidits/simple-google.git
```

## Requirements

1. Python 3.8
2. Create project at Google CLoud Platform, enable all required API for your project, save `client_secret.json` . More details 
how to [create project](https://developers.google.com/workspace/guides/create-project) and [credentials](https://developers.google.com/workspace/guides/create-credentials).
3. Set path to `client_secret.json`:
- (recommended) as env variable `SGS_CLIENTSECRET`
- copy file to `~/.sgs/client_secret.json`
- set manually `from sgs import config` `config.client_secret_file = 'path to client_secret.json file'`
4. Set full config or make separate configurations manually (config structure must be in `{"key": "value", ...}` format):
- (recommended) set path to `config.json` file as env variable `SGS_CONFIGFILE`
- copy `config.json` file to `~/.sgs/config.json`
- set manually `from sgs import config` `config.config_dict = {"scopes": "drive": ["scope_1", ...], ...}`
- manual separate configurations (only for some apps)
`from sgs import config` `config.scopes = ['scope_1', 'scope_2', ...]`
- `config.json` example:
```python
{
    "scopes": {
        "youtube": [
            "scope_1",
            "scope_2"
        ],
        "drive": [
            "scope_1",
            "scope_2"
        ]
    }
}
```

## Required scopes
Youtube
- `https://www.googleapis.com/auth/youtube.readonly`
- `https://www.googleapis.com/auth/youtube.force-ssl`

## Usage
####Recommendation: 
initialize all services that you want to use in one script. This will automatically create list of all required scopes and after first run generate `token.json` file with permissions for your project. Other way wou will probably need to delete existing `token.json` file and generate new one after each service initialized.
```python
from sgs.apps import Youtube, Drive

youtube = Youtube()
drive = Drive()
...
```
####Youtube

```python
from sgs.apps import Youtube

youtube = Youtube()
# returns list of videos objects
my_videos = youtube.my_channel.my_videos

# update user`s video on channel
video = youtube.my_channel.get_videos_by_title('foo', contains=True)[0]
video.update_video(title='bar', description='spam_eggs')

# mark selected comment as spam
for comment in video.comments:
    comment.mark_as_spam()
```

## License
[MIT](https://choosealicense.com/licenses/mit/)