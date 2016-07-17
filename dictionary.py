
#Python file for maintaining the availability status
# and
# saving special messages such as block_msg and unavaib_msg

import telebot
import config

bot = telebot.TeleBot(config.token)

#for setting the status of the admin 
def set_status(file, status):
    with open(file,"w") as text_file:
      text_file.write(str(status).lower())

#for checking the status of the admin
def check_status(file):
    with open(config.storage_availability) as f:
      z = f.read()
      if z == "unavailable":
       return "false"
      else:
       return "true"

#for setting the unavailable message for the admin
def save_msg(message, file=None):
    try:
      if file:
          unvbmsg = message.text
          with open(file,"w") as msg_file:
             msg_file.write(str(unvbmsg))
          bot.reply_to(message,"Thanks! " +"\n"+ "*The Message has been set successfully* ",parse_mode="Markdown" )
    except Exception as e:
      bot.reply_to(config.my_id, 'oooops! something went wrong')

