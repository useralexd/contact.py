#!/usr/bin/env python3

import telebot
from telebot import types
import logging

import model
import db
import config
import strings

# Initialize bot
bot = telebot.TeleBot(config.token)
telebot.logger.setLevel(logging.WARNING)


# helper decorator: wrapper around bot.message handler for catching all commands with specified prefix
def my_commandset_handler(prefix):
    def test(m):
        return (
            m.content_type == 'text' and
            m.text.startswith('/' + prefix) and
            m.chat.id == config.my_id
        )
    decorator = bot.message_handler(func=test)
    return decorator


# helper function: returns an array of InlineKeyboardButton for paginating stuff
# prefix - string added to each callback data from the front
# page_no - current page number
# pages_count - number of pages
# buttons_count - how many buttons should be returned
def pager_buttons(prefix, page_no, pages_count):
    if pages_count < 2:
        pages_count = 1
    if page_no < 1:
        page_no = 1
    if page_no > pages_count:
        page_no = pages_count

    marks = strings.pager_marks
    buttons_count = 5  # odd numbers recommended
    buttons = {}

    if pages_count > buttons_count:
        left = page_no - (buttons_count // 2)
        right = page_no + (buttons_count // 2)

        if left < 1:
            left = 1
            right = buttons_count
        if right > pages_count:
            right = pages_count
            left = pages_count - buttons_count + 1

        for i in range(left, right + 1):
            if i < page_no:
                buttons[i] = marks[1] + str(i)
            elif i == page_no:
                buttons[i] = marks[2] + str(i) + marks[2]
            elif i > page_no:
                buttons[i] = str(i) + marks[3]

        if buttons[left].startswith(marks[1]):
            del buttons[left]
            buttons[1] = marks[0] + '1'
        if buttons[right].endswith(marks[3]):
            del buttons[right]
            buttons[pages_count] = str(pages_count) + marks[4]

    else:
        for i in range(1, pages_count + 1):
            if i == page_no:
                buttons[i] = marks[2] + str(i) + marks[2]
            else:
                buttons[i] = str(i)

    button_row = [
        types.InlineKeyboardButton(
            text=buttons[key],
            callback_data=prefix + str(key)
        ) for key in sorted(buttons.keys())
        ]
    return button_row


# helper function: returns an InlineKeyboard markup for usercard
def get_usercard_markup(user, log_page=None):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    if log_page is not None:
        text = strings.msg.log_header.format(user=user)

        log_pages_count, msgs = db.msg.get_page_with(user.id, log_page)  # gets messages from db

        if log_page == 0:
            log_page = log_pages_count  # if page_no is not set, let it be the last page

        for msg in msgs:
            text += '{}\n'.format(msg)
        markup.row(*pager_buttons('log_{}_'.format(user.id), log_page, log_pages_count))
        buttons.append(types.InlineKeyboardButton(strings.btn.hide_log, callback_data='user_hide_{}'.format(user.id)))
    else:
        text = strings.msg.user_full.format(user=user)
        buttons.append(types.InlineKeyboardButton(strings.btn.show_log, callback_data='log_{}_0'.format(user.id)))

    if user.blocked:
        buttons.append(types.InlineKeyboardButton(strings.btn.unblock, callback_data='user_unblock_{}'.format(user.id)))
    else:
        buttons.append(types.InlineKeyboardButton(strings.btn.block, callback_data='user_block_{}'.format(user.id)))
    buttons.append(types.InlineKeyboardButton(strings.btn.reply, callback_data='reply_{}'.format(user.id)))

    markup.add(*buttons)
    return text, markup


# for the list of all the commands
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["start", "help"])
def command_help(message):
    bot.send_message(
        message.chat.id,
        strings.msg.help,
        parse_mode='HTML'
    )


# command for admin: Used to view the block message
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewblockmessage"])
def command_viewblockmessage(message):
    if not db.common.blockmsg:
        bot.send_message(
            message.chat.id,
            strings.msg.blockmsg_notset,
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            strings.msg.blockmsg_view.format(db.common.blockmsg),
            parse_mode="HTML"
        )


# command for admin to set the block message that the user see after getting blocked
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["setblockmessage"])
def command_setblockmessage(message):
    blockmsg = bot.send_message(
        message.chat.id,
        strings.msg.blockmsg_setting,
        parse_mode="HTML"
    )
    bot.register_next_step_handler(blockmsg, save_blockmsg)


# Next step handler for saving blockmsg
def save_blockmsg(message):
    db.common.blockmsg = str(message.text)
    bot.reply_to(
        message,
        strings.msg.blockmsg_set,
        parse_mode="HTML"
    )


# command for admin: Used to view the start message
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewstartmessage"])
def command_viewstartmessage(message):
    if not db.common.startmsg:
        bot.send_message(
            message.chat.id,
            strings.msg.startmsg_notset,
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            strings.msg.startmsg_view.format(db.common.startmsg),
            parse_mode="HTMl"
        )


# command for admin to set the start message that the user see when he starts the bot
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["setstartmessage"])
def command_setstartmessage(message):
    startmsg = bot.send_message(
        message.chat.id,
        strings.msg.startmsg_setting,
        parse_mode="HTML"
    )
    bot.register_next_step_handler(startmsg, save_startmsg)


# Next step handler for saving blockmsg
def save_startmsg(message):
    db.common.startmsg = str(message.text)
    bot.reply_to(
        message,
        strings.msg.startmsg_set,
        parse_mode="HTML"
    )


# command for admin: Used to view your Unavailable Message
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewunavailablemessage"])
def command_unavailablemessage(message):
    if not db.common.nonavailmsg:
        bot.send_message(
            message.chat.id,
            strings.msg.nonavailmsg_notset,
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            message.chat.id,
            strings.msg.nonavailmsg_view.format(db.common.nonavailmsg),
            parse_mode="HTML"
        )


# command for admin to set the message the users will see when the admin status is set to unavailable
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["setunavailablemessage"])
def command_setunavailablemessage(message):
    unvb = bot.send_message(
        message.chat.id,
        strings.msg.nonavailmsg_setting,
        parse_mode="HTML"
    )
    bot.register_next_step_handler(unvb, save_nonavailmsg)


# Next step handler for saving blockmsg
def save_nonavailmsg(message):
    db.common.nonavailmsg = str(message.text)
    bot.reply_to(
        message,
        strings.msg.nonavailmsg_set,
        parse_mode="HTML"
    )


# command for admin
# view the whole Block List containing usernames and nicknames of the blocked users, refer config.py for more info
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewblocklist"])
def command_blocklist(_):
    page_no = 1
    users = db.usr.get_blocked_page(page_no)
    s = strings.msg.blockedlist_header
    markup = types.InlineKeyboardMarkup()
    for index, user in enumerate(users):
        s += strings.msg.user_line.format(index=index, user=user)
        markup.add(
            types.InlineKeyboardButton(
                strings.btn.user.format(index=index, user=user),
                callback_data='user_show_{}'.format(user.id)
            )
        )
    markup.row(*pager_buttons('list_blocked', page_no, db.usr.get_pages_count()))
    bot.send_message(
        config.my_id,
        s,
        parse_mode='HTML',
        reply_markup=markup
    )


# handles inline keyboard buttons under the users list
@bot.callback_query_handler(func=lambda cb: cb.data.startswith('list_blocked'))
def blocked_list_pages(cb):
    page_no = int(cb.data.replace('list_blocked', '', 1))
    users = db.usr.get_blocked_page(page_no)
    s = strings.msg.blockedlist_header
    markup = types.InlineKeyboardMarkup()
    for index, user in enumerate(users):
        s += strings.msg.user_line.format(index=index, user=user)
        markup.add(
            types.InlineKeyboardButton(
                strings.btn.user.format(index=index, user=user),
                callback_data='user_show_{}'.format(user.id)
            )
        )
    markup.row(*pager_buttons('list_blocked', page_no, db.usr.get_pages_count()))
    bot.edit_message_text(
        s,
        parse_mode='HTML',
        reply_markup=markup,
        message_id=cb.message.message_id,
        chat_id=cb.from_user.id
    )
    bot.answer_callback_query(cb.id, strings.ans.done)


# command for admin: lists all non-blocked users
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["viewuserlist"])
def command_users(_):
    page_no = 1
    users = db.usr.get_page(page_no)
    s = strings.msg.userlist_header
    markup = types.InlineKeyboardMarkup()
    for index, user in enumerate(users):
        s += strings.msg.user_line.format(index=index, user=user)
        markup.add(
            types.InlineKeyboardButton(
                strings.btn.user.format(index=index, user=user),
                callback_data='user_show_{}'.format(user.id)
            )
        )
    markup.row(*pager_buttons('list_users', page_no, db.usr.get_pages_count()))
    bot.send_message(
        config.my_id,
        s,
        parse_mode='HTML',
        reply_markup=markup
    )


# handles inline keyboard buttons under the users list
@bot.callback_query_handler(func=lambda cb: cb.data.startswith('list_users'))
def user_list_pages(cb):
    page_no = int(cb.data.replace('list_users', '', 1))
    users = db.usr.get_page(page_no)
    s = strings.msg.userlist_header
    markup = types.InlineKeyboardMarkup()
    for index, user in enumerate(users):
        s += strings.msg.user_line.format(index=index, user=user)
        markup.add(
            types.InlineKeyboardButton(
                strings.btn.user.format(index=index, user=user),
                callback_data='user_show_{}'.format(user.id)
            )
        )
    markup.row(*pager_buttons('list_users', page_no, db.usr.get_pages_count()))
    bot.edit_message_text(
        s,
        parse_mode='HTML',
        reply_markup=markup,
        message_id=cb.message.message_id,
        chat_id=cb.from_user.id
    )
    bot.answer_callback_query(cb.id, strings.ans.done)


# handles inline keyboard buttons under the user_card
@bot.callback_query_handler(func=lambda cb: cb.data.startswith('user'))
def user_block_toggle(cb):
    command, _id = cb.data.split('_')[1:]
    user = db.usr.get_by_id(int(_id))  # gets user info from db
    assert user  # makes sure that user is in db

    if command == 'block':  # block command
        user.blocked = True
        bot.answer_callback_query(cb.id, strings.ans.blocked)
    elif command == 'unblock':  # unblock command
        user.blocked = False
        bot.answer_callback_query(cb.id, strings.ans.unblocked)
    else:
        bot.answer_callback_query(cb.id, strings.ans.done)

    text, markup = get_usercard_markup(user)  # edits message according to update
    bot.edit_message_text(
        text,
        parse_mode='HTML',
        reply_markup=markup,
        message_id=cb.message.message_id,
        chat_id=cb.from_user.id
    )

    db.usr.update(user)  # pushes changes to db


@bot.callback_query_handler(func=lambda cb: cb.data.startswith('log'))
def show_log(cb):
    user_id, page_no = cb.data.split('_')[1:]
    user_id = int(user_id)
    page_no = int(page_no)

    user = db.usr.get_by_id(user_id)  # gets user info from db

    text, markup = get_usercard_markup(user, page_no)

    bot.edit_message_text(
        text,
        parse_mode='HTML',
        reply_markup=markup,
        message_id=cb.message.message_id,
        chat_id=cb.from_user.id
    )
    bot.answer_callback_query(cb.id, strings.ans.done)


# a set of commands for admin to view special messages
@my_commandset_handler('msg')
def show_msg(message):
    bot.send_chat_action(message.from_user.id, action="typing")
    m_id = message.text.replace('/msg', '', 1).split()[0]
    old_msg = db.msg.get_by_shortid(m_id)
    bot.forward_message(config.my_id, old_msg.chat.id, old_msg.message_id)


# command for the admin to check his/her current status.
# The dictionary.check_status() method simply reads the text in the availability.txt file
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, commands=["checkstatus"])
def command_checkstatus(message):
    if db.common.availability == 'unavailable':
        bot.send_message(
            message.chat.id,
            strings.msg.checked_unavailable,
            parse_mode='HTML'
        )
    else:
        bot.send_message(
            message.chat.id,
            strings.msg.checked_available,
            parse_mode='HTML'
        )


# Handle always first "/start" message when new chat with your bot is created (for users other than admin)
@bot.message_handler(func=lambda message: message.chat.id != config.my_id, commands=["start"])
def command_start_all(message):
    bot.send_message(
        message.chat.id,
        db.common.startmsg.format(name=message.from_user.first_name)
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
        # if blocked: notify user about it
        bot.send_message(message.chat.id, db.common.blockmsg)

    else:
        # if not blocked:
        db.msg.create(message)  # log message in db

        text = strings.msg.new_msg.format(user=user, message=message)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(strings.btn.show_log, callback_data='log_{}_0'.format(user.id)),
            types.InlineKeyboardButton(strings.btn.block, callback_data='user_block_{}'.format(user.id)),
            types.InlineKeyboardButton(strings.btn.reply, callback_data='reply_{}'.format(user.id))
        )
        bot.send_message(  # send it to admin
            config.my_id,
            text,
            parse_mode='HTML',
            reply_markup=markup
        )

        if message.content_type != 'text':
            bot.forward_message(config.my_id, message.chat.id, message.message_id)

        # check the status of the admin whether he's available or not
        if db.common.availability == 'unavailable':
            # and notify user if unavailable
            bot.send_message(message.chat.id, db.common.nonavailmsg)


@bot.callback_query_handler(func=lambda cb: cb.data.startswith('reply_'))
def reply_to(cb):
    db.common.replying_to = int(cb.data.replace('reply_', '', 1))
    bot.answer_callback_query(cb.id, strings.ans.reply)


@bot.message_handler(
    func=lambda m: m.chat.id == config.my_id and m.chat.id not in bot.message_subscribers_next_step,
    content_types=['text']
)
def my_text(message):
    if db.common.replying_to:
        user_id = db.common.replying_to
        bot.send_chat_action(user_id, action='typing')
        bot.send_message(user_id, message.text)
        message.with_user = user_id  # mark message as belonging to conversation with specified user
        db.msg.create(message)  # log message in db
    else:
        bot.send_message(config.my_id, strings.msg.noone_to_reply)


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["sticker"])
def my_sticker(message):
    if db.common.replying_to:
        user_id = db.common.replying_to
        bot.send_chat_action(user_id, action='typing')
        bot.send_sticker(user_id, message.sticker.file_id)
        message.with_user = user_id  # mark message as belonging to conversation with specified user
        db.msg.create(message)  # log message in db
    else:
        bot.send_message(config.my_id, strings.msg.noone_to_reply)


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["photo"])
def my_photo(message):
    if db.common.replying_to:
        user_id = db.common.replying_to
        bot.send_chat_action(user_id, action='upload_photo')
        bot.send_photo(user_id, list(message.photo)[-1].file_id)
        message.with_user = user_id  # mark message as belonging to conversation with specified user
        db.msg.create(message)  # log message in db
    else:
        bot.send_message(message.chat.id, strings.msg.noone_to_reply)


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["voice"])
def my_voice(message):
    if db.common.replying_to:
        user_id = db.common.replying_to
        bot.send_voice(user_id, message.voice.file_id, duration=message.voice.duration)
        message.with_user = user_id  # mark message as belonging to conversation with specified user
        db.msg.create(message)  # log message in db
    else:
        bot.send_message(message.chat.id, strings.msg.noone_to_reply)


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["document"])
def my_document(message):
    if db.common.replying_to:
        user_id = db.common.replying_to
        bot.send_chat_action(user_id, action='upload_document')
        bot.send_document(user_id, data=message.document.file_id)
        message.with_user = user_id  # mark message as belonging to conversation with specified user
        db.msg.create(message)  # log message in db
    else:
        bot.send_message(message.chat.id, strings.msg.noone_to_reply)


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["audio"])
def my_audio(message):
    if db.common.replying_to:
        user_id = db.common.replying_to
        bot.send_chat_action(user_id, action='upload_audio')
        bot.send_audio(
            user_id,
            performer=message.audio.performer,
            audio=message.audio.file_id,
            title=message.audio.title,
            duration=message.audio.duration
        )
        message.with_user = user_id  # mark message as belonging to conversation with specified user
        db.msg.create(message)  # log message in db
    else:
        bot.send_message(message.chat.id, strings.msg.noone_to_reply)


@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["video"])
def my_video(message):
    if db.common.replying_to:
        user_id = db.common.replying_to
        bot.send_chat_action(user_id, action='upload_video')
        bot.send_video(user_id, data=message.video.file_id, duration=message.video.duration)
        message.with_user = user_id  # mark message as belonging to conversation with specified user
        db.msg.create(message)  # log message in db
    else:
        bot.send_message(message.chat.id, strings.msg.noone_to_reply)


# No Google Maps on my phone, so this function is untested, should work fine though.
@bot.message_handler(func=lambda message: message.chat.id == config.my_id, content_types=["location"])
def my_location(message):
    if db.common.replying_to:
        user_id = db.common.replying_to
        bot.send_chat_action(user_id, action='find_location')
        bot.send_location(user_id, latitude=message.location.latitude, longitude=message.location.longitude)

        message.with_user = user_id  # mark message as belonging to conversation with specified user
        db.msg.create(message)  # log message in db
    else:
        bot.send_message(message.chat.id, strings.msg.noone_to_reply)


username = bot.get_me().username
print('Bot has Started\nPlease text the bot on: @{0}\nhttps://telegram.me/{0}'.format(username))
model.replace_classes()  # replaces classes in telepot.types in order to make them db compatible
bot.send_message(config.my_id, strings.msg.bot_started)
if __name__ == '__main__':
    bot.polling(none_stop=True)
