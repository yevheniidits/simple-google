# sgs (Simple Google Services)
Simplifies interaction with Google API for most frequently used tasks

##Installation
`pip install git+https://git@github.com/yevheniidits/simple-google.git`

##Requirements
###1. Create project at Google CLoud Platform, enable APIs, save `client_secret.json` 
   more details at https://developers.google.com/workspace/guides/create-project
    and https://developers.google.com/workspace/guides/create-credentials
   
###2. Set path to `client_secret.json`:
1. (recommended) as env variable `SGS_CLIENTSECRET`
2. copy to `~/.sgs/client_secret.json`
3. set manually `from sgs import config` `config.client_secret_file = 'path to client_secret.json file'`

###3. Set full config or make separate configurations manually
####full config (structure must be {"key": "value", ...}:
1. (recommended) set path to `config.json` file as env variable `SGS_CONFIGFILE`
2. copy `config.json` file to `~/.sgs/config.json`
3. set manually `from sgs import config` `config.config_dict = {"key": "value", ...}`
#### manual separate configurations (only for some apps)
`from sgs import config` `config.scopes = ['scope_1', 'scope_2', ...]`

##Usage examples

