# -*- coding: utf-8 -*-

# Bot's token. Obtain yours from https://telegram.me/botfather
token = "TOKEN"
# Your telegram user id. Get it from @my_id_bot
my_id = 'yourid'

# Availability and messages
storage_availability = 'txtfiles/availability.txt'
storage_nonavailmsg = 'txtfiles/nonavailmsg.txt'
storage_blockmsg = 'txtfiles/blockmsg.txt'


# Database
db_auth = 'url'
db_name = 'name'

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
