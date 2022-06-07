# sgs (Simple Google Services)

Simplifies interaction with Google API for most frequently used tasks. Based on google-api-python-client.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install sgs.

```bash
pip install git+https://git@github.com/yevheniidits/simple-google.git
```

## Requirements

1. Create project at Google CLoud Platform, enable APIs, save `client_secret.json` . More details 
how to [create project](https://developers.google.com/workspace/guides/create-project) and [credentials](https://developers.google.com/workspace/guides/create-credentials).
2. Set path to `client_secret.json`:
- (recommended) as env variable `SGS_CLIENTSECRET`
- copy file to `~/.sgs/client_secret.json`
- set manually `from sgs import config` `config.client_secret_file = 'path to client_secret.json file'`
3. Set full config or make separate configurations manually (config structure must be in `{"key": "value", ...}` format):
- (recommended) set path to `config.json` file as env variable `SGS_CONFIGFILE`
- copy `config.json` file to `~/.sgs/config.json`
- set manually `from sgs import config` `config.config_dict = {"key": "value", ...}`
- manual separate configurations (only for some apps)
`from sgs import config` `config.scopes = ['scope_1', 'scope_2', ...]`

## Scopes
Youtube
- `https://www.googleapis.com/auth/youtube.readonly`
- `https://www.googleapis.com/auth/youtube.force-ssl`

## Usage
Youtube

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