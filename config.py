# -*- coding: utf-8 -*-

# Bot's token. Obtain yours from https://telegram.me/botfather
token = "<TOKEN>"
# Your telegram user id. Get it from @my_id_bot
my_id = '<your_id>'

# Availability and messages
storage_availability = 'txtfiles/availability.txt'
storage_nonavailmsg = 'txtfiles/nonavailmsg.txt'
storage_blockmsg = 'txtfiles/blockmsg.txt'


# Database
# your MongoDB connection url
db_auth = 'mongodb://<user>:<password>@<my.mongodb.com>:<port>/<database>'
db_name = '<database_name>'

try:
    from local_config import *
except ImportError:
    pass


'''
Here are things you should know:
storage_availability: stores whether admin status is "available" or "unavailable"
storage_nonavailmsg : stores the message that the user will get once the admin's status has been set to unavailable
storage_blockmsg    : stores the message that the user will see once he/she is blocked

'''
