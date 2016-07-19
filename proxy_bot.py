#!/usr/bin/env python3

import telebot
import os

import model
import db
import config
import dictionary

# Initialize bot
bot = telebot.TeleBot(config.token)


# for the list of all the commands
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["help"])
def command_help(message):
    bot.send_message(
        message.chat.id,
        """*Hey """ + message.chat.first_name +
        """!\nSo, here is a list of commands that you should keep in mind:* \n
`1`- /available  : sets your current status as available
`2`- /unavailable: sets your current status as unavailable 
`3`- /viewunavailablemessage : to view your Unavailable Message
`4`- /setunavailablemessage  : set the text message that you want users to see when you're unavailable 
`5`- /checkstatus: allows your to check your current status
`6`- /block `@username/nickname`  : allows you to block a user
`7`- /unblock `@username/nickname`: allows you to unblock a blocked user
`8`- /viewblockmessage: to view the block message (that the users will see)
`9`- /setblockmessage : set the text message that you want users to see when they are blocked
`10`-/viewblocklist  : allows you to view the list of blocked users
`11`-/viewnicknames  : allows you to view all the nicknames (with Firstname as reference)\n
*For any help and queries please contact -* [me](telegram.me/mrgigabytebot) *or check out* [this](https://github.com/mrgigabyte/proxybot)""",
        parse_mode="Markdown"
    )


# command for admin: Used to view the block message
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewblockmessage"])
def command_viewblockmessage(message):
    with open(config.storage_blockmsg) as f:
        if os.stat(config.storage_blockmsg).st_size == 0:
            bot.send_message(
                message.chat.id,
                """*Oops!*
You haven't set any *Block Message* for the users. 
To set one kindly send: /setblockmessage to me""",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                message.chat.id,
                "`Your Block Message:`" + "\n" + f.read(),
                parse_mode="Markdown"
            )


# command for admin to set the block message that the user after getting blocked
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["setblockmessage"])
def command_setblockmessage(message):
    blockmsg = bot.send_message(
        message.chat.id,
        "Alright now send me your text that you want the user to see when he/she is *blocked*",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(blockmsg, lambda m: dictionary.save_msg(m, file=config.storage_blockmsg))


# command for admin
# view all the nicknames in the format --> nick-name : user first name
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewnicknames"])
def command_nicknamelist(message):
    raise NotImplementedError
    # with open(config.storage_fnamelist) as f:
    #    if os.stat(config.storage_fnamelist).st_size == 0:
    #       bot.send_message(message.chat.id, "No nicknames yet!")
    #    else:
    #       bot.send_message(message.chat.id,"`Nick Names:`" +"\n"+ "`(nick name: first name)`"+"\n"+ f.read(), parse_mode="Markdown")


# command for admin
# view the whole Block List containing usernames and nicknames of the blocked users, refer config.py for more info
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewblocklist"])
def command_blocklist(message):
    raise NotImplementedError
    # with open(config.storage_blocklist) as f:
    #    if os.stat(config.storage_blocklist).st_size == 0:
    #       bot.send_message(message.chat.id, "No user is blocked!")
    #    else:
    #       bot.send_message(message.chat.id,"`Block List:`"+"\n"+ f.read(), parse_mode="Markdown")


# command for admin: Used to view your Unavailable Message
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewunavailablemessage"])
def command_unavailablemessage(message):
    with open(config.storage_nonavailmsg) as f:
        if os.stat(config.storage_nonavailmsg).st_size == 0:
            bot.send_message(
                message.chat.id,
                """*Oops!*
You haven't set any Unavailable message for the users. 
To set one kindly send: /setunavailablemessage to me""",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                message.chat.id,
                "`Your Unavailable Message:`" + "\n" + f.read(),
                parse_mode="Markdown"
            )


# Handle always first "/start" message when new chat with your bot is created (for users other than admin)
@bot.message_handler(func=lambda message: message.chat.id != config.my_id, commands=["start"])
def command_start_all(message):
    bot.send_message(
        message.chat.id,
        "Hey " + message.chat.first_name + "!" + "\n" +
        " Write me your text and the admin will get in touch with you shortly."
    )


# command for admin to set the message the users will see when the admin status is set to unavailable
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["setunavailablemessage"])
def command_setunavailablemessage(message):
    unvb = bot.send_message(
        message.chat.id,
        "Alright now send me your text that you want others to see when you're *unavailable*",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(unvb, lambda m: dictionary.save_msg(m, file=config.storage_nonavailmsg))


# command for admin to set his/her status as available
# this will simply re-write the availability.txt file with the text "available"
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["available"])
def command_available(message):
    bot.send_message(
        message.chat.id,
        "Your Status has been set as *Available*",
        parse_mode="Markdown"
    )
    dictionary.set_status(config.storage_availability, "Available")


# command for admin to set his/her status as unavailable
# this will simply re-write the availability.txt file with the text "unavailable"
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["unavailable"])
def command_unavailable(message):
    bot.send_message(
        message.chat.id,
        "Your Status has been set as *Unavailable*",
        parse_mode="Markdown"
    )
    dictionary.set_status(config.storage_availability, "Unavailable")


# command for the admin to check his/her current status.
# The dictionary.check_status() method simply reads the text in the availability.txt file
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["checkstatus"])
def command_checkstatus(message):
    ww = dictionary.check_status(config.storage_availability)
    if ww == "false":
        bot.send_message(
            message.chat.id,
            "Your current status  is *Unavailable*",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            message.chat.id,
            "Your current status  is *Available*",
            parse_mode="Markdown"
        )


# Handle the messages which are not sent by the admin user(the one who is handling the bot)
# Sends texts, audios, document etc to the admin
@bot.message_handler(
    func=lambda message: message.chat.id != config.my_id,
    content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'voice', 'location', 'contact']
)
def handle_or_block(message):
    user = db.usr.get_by_id(message.from_user.id)  # get user from database
    if not user:  # If user is new
        user = model.User(_id=message.from_user.id, first_name=message.from_user.first_name)  # creates user model
    user.update(message.from_user)  # updates user data (username, first_name and last_name)
    db.usr.update(user)  # pushes updated data back to db

    # checks whether the admin has blocked that user via bot or not
    if user.blocked:
        with open(config.storage_blockmsg) as t:
            bot.send_message(message.chat.id, t.read())

    else:
        # forwards the message sent by the user to the admin. Only if the user is not blocked
        # checks if the user has replied to any previously send message.
        # If yes ---> Then it checks the format and sends that text again to the admin
        # If no ----> Then it simply forwards the message to the admin
        db.msg.create(message)
        text, markup = get_user_card(user)
        bot.send_message(config.my_id, text, reply_markup=markup)
        if message.reply_to_message:
            if message.reply_to_message.text:
                text = message.reply_to_message.text
                bot.send_message(
                    config.my_id,
                    "<b>" + message.chat.first_name + " replied to: " + "</b>" + text,
                    parse_mode="HTML"
                )
            elif message.reply_to_message.sticker:
                m = message.reply_to_message.sticker.file_id
                bot.send_message(
                    config.my_id,
                    "<b>" + message.chat.first_name + " replied to sticker" + "</b>",
                    parse_mode="HTML"
                )
                bot.send_sticker(config.my_id, m)
            elif message.reply_to_message.audio:
                audio = message.reply_to_message.audio
                m = audio.file_id
                bot.send_message(
                    config.my_id,
                    "<b>" + message.chat.first_name + " replied to audio" + "</b>",
                    parse_mode="HTML"
                )
                bot.send_audio(
                    config.my_id,
                    performer=audio.performer,
                    audio=m,
                    title=audio.title,
                    duration=audio.duration
                )
            elif message.reply_to_message.document:
                m = message.reply_to_message.document.file_id
                bot.send_document(config.my_id, m, caption=message.chat.first_name + " replied to ")
            elif message.reply_to_message.photo:
                m = message.reply_to_message.photo[-1].file_id
                bot.send_photo(config.my_id, m, caption=message.chat.first_name + " replied to ")
            elif message.reply_to_message.video:
                m = message.reply_to_message.video.file_id
                bot.send_video(config.my_id, m, caption=message.chat.first_name + " replied to ")
            elif message.reply_to_message.voice:
                m = message.reply_to_message.voice.file_id
                bot.send_message(
                    config.my_id,
                    "<b>" + message.chat.first_name + " replied to Voice Note" + "</b>",
                    parse_mode="HTML"
                )
                bot.send_voice(config.my_id, m)
            elif message.reply_to_message.location:
                location = message.reply_to_message.location
                bot.send_message(
                    config.my_id,
                    "<b>" + message.chat.first_name + " replied to Location" + "</b>",
                    parse_mode="HTML"
                )
                bot.send_location(config.my_id, latitude=location.latitude, longitude=location.longitude)
            elif message.reply_to_message.contact:
                contact = message.reply_to_message.contact
                m = contact[-1].file_id
                bot.send_message(
                    config.my_id,
                    "<b>" + message.chat.first_name + " replied to Contact" + "</b>",
                    parse_mode="HTML"
                )
                bot.send_contact(config.my_id, m, first_name=contact.first_name)
        bot.forward_message(config.my_id, message.chat.id, message.message_id)

        # checks the status of the admin whether he's available or not
        q = dictionary.check_status(config.storage_availability)
        if q == "false":
            with open(config.storage_nonavailmsg) as m:
                bot.send_message(message.chat.id, m.read())


def get_user_card(user):
    text = ''
    if user.username:
        text += '@' + user.username
    text += '''
Id: {id}
First name: {first}
Last name: {last}
    '''.format(id=user.id, first=user.first_name, last=user.last_name or '_None_')
    if user.blocked:
        text += 'BLOCKED'

    markup = telebot.types.InlineKeyboardMarkup()
    if user.blocked:
        markup.add(telebot.types.InlineKeyboardButton('Unblock', callback_data='un' + user.id))
    else:
        markup.add(telebot.types.InlineKeyboardButton('Block', callback_data='ub' + user.id))

    return text, markup


# handles inline keyboard buttons under the user_card
@bot.callback_query_handler(func=lambda cb: cb.data.startswith('u'))
def user_block_toggle(cb):
    user = db.usr.get_by_id(cb.data[2:])  # gets user info from db
    assert user  # makes sure that user is in db
    user.update(cb.from_user)  # updates user data (username, first_name and last_name)

    if cb.data[1] == 'b':  # block command
        user.blocked = True
    elif cb.data[1] == 'n':  # unblock command
        user.blocked = False
    text, markup = get_user_card(user)
    # edits message according to update
    bot.edit_message_text(text, reply_markup=markup, message_id=cb.message.message_id, chat_id=cb.from_user.id)
    db.usr.update(user)  # pushes changes to db


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["text"])
def my_text(message):
    # If we're just sending messages to bot (not replying) -> do nothing and notify about it.
    # Else -> get ID whom to reply and send message FROM bot.
    if message.reply_to_message:
        if not message.reply_to_message.forward_from:
            bot.send_message(
                config.my_id,
                "*Oops! Something went wrong make sure you're replying to the right person!*",
                parse_mode="Markdown"
            )
        else:
            user_id = message.reply_to_message.forward_from.id
            bot.send_chat_action(user_id, action='typing')
            bot.send_message(user_id, message.text)

    else:
        handle_or_block(message)  # FIXME: TEMP FOR DEBUG, REPLACE WITH FOLLOWING LINE
        # bot.send_message(config.my_id,"No one to reply!")

            
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["sticker"])
def my_sticker(message):
    # If we're just sending messages to bot (not replying) -> do nothing and notify about it.
    # Else -> get ID whom to reply and send message FROM bot.
    if message.reply_to_message:
        if not message.reply_to_message.forward_from:
            bot.send_message(
                config.my_id,
                "*Oops! Something went wrong make sure you're replying to the right person!*",
                parse_mode="Markdown"
            )
        else:
            chat_id = message.reply_to_message.forward_from.id
            bot.send_chat_action(chat_id, action='typing')
            bot.send_sticker(chat_id, message.sticker.file_id)
    else:
        bot.send_message(config.my_id, "No one to reply")


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["photo"])
def my_photo(message):
    if message.reply_to_message:
        if not message.reply_to_message.forward_from:
            bot.send_message(
                config.my_id,
                "*Oops! Something went wrong make sure you're replying to the right person!*",
                parse_mode="Markdown"
            )
        else:
            who_to_send_id = message.reply_to_message.forward_from.id
            bot.send_chat_action(who_to_send_id, action='upload_photo')
            bot.send_photo(who_to_send_id, list(message.photo)[-1].file_id)
    else:
        bot.send_message(message.chat.id, "No one to reply!")


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["voice"])
def my_voice(message):
    if message.reply_to_message:
        if not message.reply_to_message.forward_from:
            bot.send_message(
                config.my_id,
                "*Oops! Something went wrong make sure you're replying to the right person!*",
                parse_mode="Markdown"
            )
        else:
            who_to_send_id = message.reply_to_message.forward_from.id
            bot.send_voice(who_to_send_id, message.voice.file_id, duration=message.voice.duration)
    else:
        bot.send_message(message.chat.id, "No one to reply!")


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["document"])
def my_document(message):
    if message.reply_to_message:
        if not message.reply_to_message.forward_from:
            bot.send_message(
                config.my_id,
                "*Oops! Something went wrong make sure you're replying to the right person!*",
                parse_mode="Markdown"
            )
        else:
            who_to_send_id = message.reply_to_message.forward_from.id
            bot.send_chat_action(who_to_send_id, action='upload_document')
            bot.send_document(who_to_send_id, data=message.document.file_id)
    else:
        bot.send_message(message.chat.id, "No one to reply!")


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["audio"])
def my_audio(message):
    if message.reply_to_message:
        if not message.reply_to_message.forward_from:
            bot.send_message(
                config.my_id,
                "*Oops! Something went wrong make sure you're replying to the right person!*",
                parse_mode="Markdown"
            )
        else:
            who_to_send_id = message.reply_to_message.forward_from.id
            bot.send_chat_action(who_to_send_id, action='upload_audio')
            bot.send_audio(who_to_send_id, performer=message.audio.performer,
                           audio=message.audio.file_id, title=message.audio.title,
                           duration=message.audio.duration)
    else:
        bot.send_message(message.chat.id, "No one to reply!")


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["video"])
def my_video(message):
    if message.reply_to_message:
        if not message.reply_to_message.forward_from:
            bot.send_message(
                config.my_id,
                "*Oops! Something went wrong make sure you're replying to the right person!*",
                parse_mode="Markdown"
            )
        else:
            who_to_send_id = message.reply_to_message.forward_from.id
            bot.send_chat_action(who_to_send_id, action='upload_video')
            bot.send_video(who_to_send_id, data=message.video.file_id, duration=message.video.duration)
    else:
        bot.send_message(message.chat.id, "No one to reply!")


# No Google Maps on my phone, so this function is untested, should work fine though.
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["location"])
def my_location(message):
    if message.reply_to_message:
        if not message.reply_to_message.forward_from:
            bot.send_message(
                config.my_id,
                "*Oops! Something went wrong make sure you're replying to the right person!*",
                parse_mode="Markdown"
            )
        else:
            who_to_send_id = message.reply_to_message.forward_from.id
            bot.send_chat_action(who_to_send_id, action='find_location')
            bot.send_location(who_to_send_id, latitude=message.location.latitude, longitude=message.location.longitude)
    else:
        bot.send_message(message.chat.id, "No one to reply!")

print('Bot has Started\nPlease text the bot on:@{}'.format(bot.get_me().username))
model.replace_classes()  # replaces classes in telepot.types in order to make them db compatible
bot.send_message(config.my_id, 'Bot Started')
if __name__ == '__main__':
    bot.polling(none_stop=True)
