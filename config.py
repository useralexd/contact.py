# Bot's token. Obtain yours from https://telegram.me/botfather
token = "<TOKEN>"
# Your telegram user id. Get it from @my_id_bot
my_id = '<your_id>'


# Database
# your MongoDB connection url
db_auth = 'mongodb://<user>:<password>@<my.mongodb.com>:<port>/<database>'
db_name = '<database_name>'

# Smart availability: your available status will expire after this amount of seconds
availability_expiration = 60 * 60  # 1h

# When you click `Reply` button, your replying state will expire after this amount of seconds
replying_expiration = 15 * 60  # 15min


# You can define all those variables in local_config.py
# It will let you `git pull` without merging
# Take care that updates are not guaranteed to be backward compatible
try:
    from local_config import *
except ImportError:
    pass
