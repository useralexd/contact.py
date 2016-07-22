# -*- coding: utf-8 -*-

# Bot's token. Obtain yours from https://telegram.me/botfather
token = "<TOKEN>"
# Your telegram user id. Get it from @my_id_bot
my_id = '<your_id>'


# Database
# your MongoDB connection url
db_auth = 'mongodb://<user>:<password>@<my.mongodb.com>:<port>/<database>'
db_name = '<database_name>'

try:
    from local_config import *
except ImportError:
    pass
