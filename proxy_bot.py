#!/usr/bin/env python3

import telebot

import model
import db
import config

# Initialize bot
bot = telebot.TeleBot(config.token)


# helper function: returns an array of InlineKeyboardButton for paginating stuff
# prefix - string added to each callback data from the front
# page_no - current page number
# pages_count - number of pages
# buttons_count - how many buttons should be returned
def pager_buttons(prefix, page_no, pages_count, buttons_count=5):
    marks = ['« ', '< ', '·', ' >', ' »', ' - ']
    buttons = {}

    left = page_no - (buttons_count // 2)
    right = page_no + (buttons_count // 2)
    if pages_count >= buttons_count:
        if left < 1:
            left = 1
        if left == 1:
            right = buttons_count
        if right > pages_count:
            right = pages_count
        if right == pages_count:
            left = pages_count - buttons_count + 1

    for i in range(left, right + 1):
        if 0 < i <= pages_count:
            if i < page_no:
                buttons[i] = marks[1] + str(i)
            if i == page_no:
                buttons[i] = marks[2] + str(i) + marks[2]
            if i > page_no:
                buttons[i] = str(i) + marks[3]
        else:
            buttons[i] = marks[5]

    if buttons[left].startswith(marks[1]):
        del buttons[left]
        buttons[1] = marks[0] + '1'
    if buttons[right].endswith(marks[3]):
        del buttons[right]
        buttons[pages_count] = str(pages_count) + marks[4]

    button_row = [
        telebot.types.InlineKeyboardButton(
            text=buttons[key],
            callback_data=prefix + (str(key) if buttons[key] != marks[5] else '')
        ) for key in sorted(buttons.keys())
        ]
    return button_row


# for the list of all the commands
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["start", "help"])
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
`6`- /viewblockmessage: to view the block message (that the users will see)
`7`- /setblockmessage : set the text message that you want users to see when they are blocked
`8`- /viewblocklist  : allows you to view the list of blocked users
`9`- /viewuserlist  : allows you to view all non-blocked users in database
`10`- /setstartmessage  : set the text message that you want users to see when they start the bot
`11`- /viewstartmessage  : to view the Start Message
\n
*For any help and queries please contact -* [me](telegram.me/phash_bot) *or check out* [source code](https://github.com/p-hash/proxybot)""",
        parse_mode="Markdown"
    )


# command for admin: Used to view the block message
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewblockmessage"])
def command_viewblockmessage(message):
    if not db.common.blockmsg:
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
            "`Your Block Message:`" + "\n" + db.common.blockmsg,
            parse_mode="Markdown"
        )


# command for admin to set the block message that the user see after getting blocked
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["setblockmessage"])
def command_setblockmessage(message):
    blockmsg = bot.send_message(
        message.chat.id,
        "Alright now send me your text that you want the user to see when he/she is *blocked*",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(blockmsg, save_blockmsg)


# Next step handler for saving blockmsg
def save_blockmsg(message):
    db.common.blockmsg = str(message.text)
    bot.reply_to(
        message,
        "Thanks! " + "\n" + "*The new Block Message has been set successfully* ",
        parse_mode="Markdown"
    )


# command for admin: Used to view the start message
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewstartmessage"])
def command_viewstartmessage(message):
    if not db.common.startmsg:
        bot.send_message(
            message.chat.id,
            """*Oops!*
You haven't set any *Start Message* for the users.
To set one kindly send: /setstartmessage to me""",
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            message.chat.id,
            "`Your Start Message:`" + "\n" + db.common.startmsg,
            parse_mode="Markdown"
        )


# command for admin to set the start message that the user see when he starts the bot
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["setstartmessage"])
def command_setstartmessage(message):
    startmsg = bot.send_message(
        message.chat.id,
        "Alright now send me your text that you want the user to see when he/she *starts* the bot",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(startmsg, save_startmsg)


# Next step handler for saving blockmsg
def save_startmsg(message):
    db.common.startmsg = str(message.text)
    bot.reply_to(
        message,
        "Thanks! " + "\n" + "*The new Start Message has been set successfully* ",
        parse_mode="Markdown"
    )


# command for admin
# view the whole Block List containing usernames and nicknames of the blocked users, refer config.py for more info
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewblocklist"])
def command_blocklist(message):
    bot.send_chat_action(message.from_user.id, "typing")
    if not db.usr.count:
        bot.send_message(config.my_id, "You haven't blocked any users yet!")
        return
    users = db.usr.get_blocked_page()
    s = "Blocked list: \n\n"
    for user in users:
        s += '{}\n'.format(user)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(*pager_buttons('lb', 1, db.usr.get_pages_count()))
    bot.send_message(config.my_id, s, reply_markup=markup)


# handles inline keyboard buttons under the users list
@bot.callback_query_handler(func=lambda cb: cb.data.startswith('lb'))
def blocked_list_pages(cb):
    page_no = int(cb.data.lstrip('lb'))
    users = db.usr.get_page(page_no)
    s = "Blocked list: \n\n"
    for user in users:
        s += '{}'.format(user) + '\n'
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(*pager_buttons('lb', page_no, db.usr.get_pages_count()))
    bot.edit_message_text(
        s,
        reply_markup=markup,
        message_id=cb.message.message_id,
        chat_id=cb.from_user.id
    )
    bot.answer_callback_query(cb.id, 'Done!')


# command for admin: lists all non-blocked users
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewuserlist"])
def command_users(message):
    bot.send_chat_action(message.from_user.id, "typing")
    if not db.usr.count:
        bot.send_message(config.my_id, "No users in database!")
        return
    users = db.usr.get_page()
    s = "User list: \n\n"
    for user in users:
        s += '{}\n'.format(user)
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(*pager_buttons('lu', 1, db.usr.get_pages_count()))
    bot.send_message(config.my_id, s, reply_markup=markup)


# handles inline keyboard buttons under the users list
@bot.callback_query_handler(func=lambda cb: cb.data.startswith('lu'))
def user_list_pages(cb):
    page_no = int(cb.data.lstrip('lu'))
    users = db.usr.get_page(page_no)
    s = "User list: \n\n"
    for user in users:
        s += '{}'.format(user) + '\n'
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(*pager_buttons('lu', page_no, db.usr.get_pages_count()))
    bot.edit_message_text(
        s,
        reply_markup=markup,
        message_id=cb.message.message_id,
        chat_id=cb.from_user.id
    )
    bot.answer_callback_query(cb.id, 'Done!')


# a set of commands for admin to view user's cards
@bot.message_handler(func=lambda m: m.text.startswith('/user') and m.chat.id == config.my_id, content_types=['text'])
def show_user(message):
    bot.send_chat_action(message.from_user.id, action="typing")
    uid = int(message.text.lstrip('/user').split()[0])
    user = db.usr.get_by_id(uid)
    if user:
        text = '{:full}'.format(user)
        markup = telebot.types.InlineKeyboardMarkup()
        if user.blocked:
            markup.add(telebot.types.InlineKeyboardButton('Unblock', callback_data='un' + str(user.id)))
        else:
            markup.add(telebot.types.InlineKeyboardButton('Block', callback_data='ub' + str(user.id)))
    else:
        text = "Invalid command"
        markup = None
    bot.send_message(config.my_id, text, reply_markup=markup)


# handles inline keyboard buttons under the user_card
@bot.callback_query_handler(func=lambda cb: cb.data.startswith('u'))
def user_block_toggle(cb):
    user = db.usr.get_by_id(int(cb.data[2:]))  # gets user info from db
    assert user  # makes sure that user is in db

    if cb.data[1] == 'b':  # block command
        user.blocked = True
    elif cb.data[1] == 'n':  # unblock command
        user.blocked = False

    text = '{:full}'.format(user)
    markup = telebot.types.InlineKeyboardMarkup()
    if user.blocked:
        markup.add(telebot.types.InlineKeyboardButton('Unblock', callback_data='un' + str(user.id)))
    else:
        markup.add(telebot.types.InlineKeyboardButton('Block', callback_data='ub' + str(user.id)))

    # edits message according to update
    bot.edit_message_text(text, reply_markup=markup, message_id=cb.message.message_id, chat_id=cb.from_user.id)
    bot.answer_callback_query(cb.id, 'Done')
    db.usr.update(user)  # pushes changes to db


# command for admin: Used to view your Unavailable Message
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewunavailablemessage"])
def command_unavailablemessage(message):
    if not db.common.nonavailmsg:
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
            "`Your Unavailable Message:`" + "\n" + db.common.nonavailmsg,
            parse_mode="Markdown"
        )


# command for admin to set the message the users will see when the admin status is set to unavailable
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["setunavailablemessage"])
def command_setunavailablemessage(message):
    unvb = bot.send_message(
        message.chat.id,
        "Alright now send me your text that you want others to see when you're *unavailable*",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(unvb, save_nonavailmsg)


# Next step handler for saving blockmsg
def save_nonavailmsg(message):
    db.common.nonavailmsg = str(message.text)
    bot.reply_to(
        message,
        "Thanks! " + "\n" + "*The new Unavailable Message has been set successfully* ",
        parse_mode="Markdown"
    )


# command for admin to set his/her status as available
# this will simply re-write the availability.txt file with the text "available"
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["available"])
def command_available(message):
    bot.send_message(
        message.chat.id,
        "Your Status has been set as *Available*",
        parse_mode="Markdown"
    )
    db.common.availability = 'available'


# command for admin to set his/her status as unavailable
# this will simply re-write the availability.txt file with the text "unavailable"
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["unavailable"])
def command_unavailable(message):
    bot.send_message(
        message.chat.id,
        "Your Status has been set as *Unavailable*",
        parse_mode="Markdown"
    )
    db.common.availability = 'unavailable'


# command for the admin to check his/her current status.
# The dictionary.check_status() method simply reads the text in the availability.txt file
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["checkstatus"])
def command_checkstatus(message):
    if db.common.availability == 'unavailable':
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


# Handle always first "/start" message when new chat with your bot is created (for users other than admin)
@bot.message_handler(func=lambda message: message.chat.id != config.my_id, commands=["start"])
def command_start_all(message):
    bot.send_message(
        message.chat.id,
        "Hey " + message.chat.first_name + "!\n" + db.common.startmsg
    )


# Handle the messages which are not sent by the admin user(the one who is handling the bot)
# Sends texts, audios, document etc to the admin
@bot.message_handler(
    func=lambda message: message.chat.id != config.my_id,
    content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'voice', 'location', 'contact']
)
def handle_all(message):
    user = db.usr.get_by_id(message.from_user.id)  # get user from database
    if not user:  # If user is new
        user = model.User(_id=message.from_user.id, first_name=message.from_user.first_name)  # creates user model
    user.update(message.from_user)  # updates user data (username, first_name and last_name)
    db.usr.update(user)  # pushes updated data back to db

    # checks whether the admin has blocked that user via bot or not
    if user.blocked:
        bot.send_message(message.chat.id, db.common.blockmsg)

    else:
        # forwards the message sent by the user to the admin. Only if the user is not blocked
        # checks if the user has replied to any previously send message.
        # If yes ---> Then it checks the format and sends that text again to the admin
        # If no ----> Then it simply forwards the message to the admin
        db.msg.create(message)  # log message in db

        text = '{:full}'.format(user)
        markup = telebot.types.InlineKeyboardMarkup()
        if user.blocked:
            markup.add(telebot.types.InlineKeyboardButton('Unblock', callback_data='un' + str(user.id)))
        else:
            markup.add(telebot.types.InlineKeyboardButton('Block', callback_data='ub' + str(user.id)))

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
        if db.common.availability == 'unavailable':
            bot.send_message(message.chat.id, db.common.nonavailmsg)


@bot.message_handler(
    func=lambda m: m.chat.id == config.my_id and m.chat.id not in bot.message_subscribers_next_step,
    content_types=['text']
)
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
            db.msg.create(message)  # log message in db
    else:
        bot.send_message(config.my_id,"No one to reply!")


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
            db.msg.create(message)  # log message in db
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
            db.msg.create(message)  # log message in db
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
            db.msg.create(message)  # log message in db
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
            db.msg.create(message)  # log message in db
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
            bot.send_audio(
                who_to_send_id,
                performer=message.audio.performer,
                audio=message.audio.file_id,
                title=message.audio.title,
                duration=message.audio.duration
            )
            db.msg.create(message)  # log message in db
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
            db.msg.create(message)  # log message in db
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
            db.msg.create(message)  # log message in db
    else:
        bot.send_message(message.chat.id, "No one to reply!")


print('Bot has Started\nPlease text the bot on:@{}'.format(bot.get_me().username))
model.replace_classes()  # replaces classes in telepot.types in order to make them db compatible
bot.send_message(config.my_id, 'Bot Started')
if __name__ == '__main__':
    bot.polling(none_stop=True)
