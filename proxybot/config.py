import os

# To configure bot specify these environment variables:

# PROXYBOT_TOKEN - Bot's token. Obtain yours from https://telegram.me/botfather
# PROXYBOT_MY_ID - Your telegram user id. Get it from @my_id_bot (for single proxybot instanse)


# PROXYBOT_DB_AUTH - Your MongoDB connection url in form: 
#   'mongodb://<user>:<password>@<my.mongodb.com>:<port>/<database>'
# PROXYBOT_DB_NAME - database name

# PROXYBOT_AVAILABILITY_EXPIRATION - Smart availability: 
#   Your available status will expire after this amount of seconds
availability_expiration = 60 * 60  # 1h - default value

# PROXYBOT_REPLYING_EXPIRATION
#   When you click `Reply` button, your replying state will expire after this amount of seconds
replying_expiration = 15 * 60  # 15min - default value


# Webhook settings (for webhook and masterbot)
# PROXYBOT_PUBLIC_HOST - Your public ip or domain (example.com)
public_host = ''
# PROXYBOT_LISTEN_HOST - Host the server would listen on (0.0.0.0)
listen_host = host = '0.0.0.0' # default value
# PROXYBOT_PORT - one of [80, 88, 443, 8443]
port = 443 # default value

cert = None  # or '/path/to/cert.pem'
key = None  # or '/path/to/key.pem'
ssl_context = (cert, key)  # or None

# You can define all those variables in local_config.py
# It will let you `git pull` without merging
# Take care that updates are not guaranteed to be backward compatible
try:
    from local_config import *
except ImportError:
    pass

for k,v in os.environ.items():
    if k.startswith("PROXYBOT_"):
        key = k.split('_', 1)[1:]
        key = '_'.join(key).lower()
        locals()[key] = v

baseurl = 'https://{}:{}/'.format(public_host, port)
