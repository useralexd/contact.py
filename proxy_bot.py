#!/usr/bin/env python3

import telebot
from telebot import types
import logging

import model
import db
import config
import strings

telebot.logger.setLevel(logging.WARNING)


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


class ProxyBot(telebot.TeleBot):
    def __init__(self, token, my_id):
        super().__init__(token)
        bot = self
        self.my_id = my_id

        # helper decorator: wrapper around bot.message handler for catching all commands with specified prefix
        def my_commandset_handler(prefix):
            def test(m):
                return (
                    m.content_type == 'text' and
                    m.text.startswith('/' + prefix) and
                    m.chat.id == my_id
                )

            decorator = bot.message_handler(func=test)
            return decorator

        # for the list of all the commands
        @bot.message_handler(func=lambda message: message.chat.id == my_id, commands=["start", "help"])
        def command_help(message):
            if db.common.messages:
                bot.send_message(
                    my_id,
                    strings.msg.help.format(first_name=message.from_user.first_name),
                    parse_mode='HTML'
                )
            else:
                master_start(message)

        @bot.message_handler(func=lambda message: message.chat.id == my_id, commands=['messages'])
        def master_start(_):
            db.common.state = 'set_start'
            send_state()

        @bot.message_handler(func=lambda m: db.common.state.startswith('set'))
        def master_step(message):
            if message.content_type == 'text':
                msg_type = db.common.state.split('_')[1]
                old_msg = db.common.messages.get(msg_type)
                new_msg = str(message.text)
                db.common.messages[msg_type] = new_msg  # save to db
                db.common.save()
                prev_step_msg = db.common.prev_msg

                # edit previous
                if old_msg:
                    text = strings.msg.master_edited.format(
                        msg_type=msg_type,
                        old_msg=old_msg,
                        new_msg=new_msg
                    )
                else:
                    text = strings.msg.master_set.format(
                        msg_type=msg_type,
                        new_msg=new_msg
                    )
                bot.edit_message_text(
                    text,
                    chat_id=prev_step_msg.chat.id,
                    message_id=prev_step_msg.message_id,
                    reply_markup=None,
                    parse_mode='HTML'
                )

                # set state
                db.common.state = {
                    'set_start': 'set_unavailable',
                    'set_unavailable': 'set_block',
                    'set_block': 'none'
                }[db.common.state]

                send_state()
            else:
                bot.reply_to(message, strings.msg.invalid_content_type)

        def send_state():
            if db.common.state.startswith('set'):
                msg_type = db.common.state.split('_')[1]
                markup = types.InlineKeyboardMarkup()
                buttons = list()
                if msg_type != 'start':
                    buttons.append(types.InlineKeyboardButton(strings.btn.back, callback_data='back'))

                if db.common.messages.get(msg_type):
                    text = strings.msg.master_step.format(
                        msg_type=msg_type,
                        msg=db.common.messages[msg_type]
                    )
                    buttons.append(types.InlineKeyboardButton(strings.btn.skip, callback_data='skip'))
                else:
                    text = strings.msg.master_notset.format(msg_type=msg_type)

                markup.add(*buttons)
                db.common.prev_msg = bot.send_message(
                    my_id,
                    text,
                    reply_markup=markup,
                    parse_mode='HTML'
                )
            else:
                bot.send_message(
                    my_id,
                    strings.msg.master_done,
                    parse_mode='HTML'
                )
                db.common.prev_msg = None

        @bot.callback_query_handler(func=lambda cb: cb.data == 'skip')
        def master_skip(cb):
            if cb.message.message_id == db.common.prev_msg.message_id:
                msg_type = db.common.state.split('_')[1]
                old_msg = db.common.messages.get(msg_type)
                bot.edit_message_text(
                    strings.msg.master_skipped.format(
                        msg_type=msg_type,
                        msg=old_msg
                    ),
                    chat_id=cb.message.chat.id,
                    message_id=cb.message.message_id,
                    reply_markup=None,
                    parse_mode='HTML'
                )

                # set state
                db.common.state = {
                    'set_start': 'set_unavailable',
                    'set_unavailable': 'set_block',
                    'set_block': 'none'
                }[db.common.state]

                send_state()
                bot.answer_callback_query(cb.id, strings.ans.skipped)
            else:
                bot.answer_callback_query(cb.id, strings.ans.error)

        @bot.callback_query_handler(func=lambda cb: cb.data == 'back')
        def master_back(cb):
            if cb.message.message_id == db.common.prev_msg.message_id:
                msg_type = db.common.state.split('_')[1]
                old_msg = db.common.messages.get(msg_type)
                bot.edit_message_text(
                    strings.msg.master_skipped.format(
                        msg_type=msg_type,
                        msg=old_msg
                    ),
                    chat_id=cb.message.chat.id,
                    message_id=cb.message.message_id,
                    reply_markup=None,
                    parse_mode='HTML'
                )

                # set state
                db.common.state = {
                    'set_unavailable': 'set_start',
                    'set_block': 'set_unavailable'
                }[db.common.state]

                send_state()
                bot.answer_callback_query(cb.id, strings.ans.returned)
            else:
                bot.answer_callback_query(cb.id, strings.ans.error)

        # command for admin
        # view the whole Block List
        @bot.message_handler(func=lambda message: message.chat.id == my_id, commands=["viewblocklist"])
        def command_blocklist(_):
            page_no = 1
            pages_count, users = db.usr.get_blocked_page(page_no)
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
            markup.row(*pager_buttons('list_blocked', page_no, pages_count))
            bot.send_message(
                my_id,
                s,
                parse_mode='HTML',
                reply_markup=markup
            )

        # handles inline keyboard buttons under the users list
        @bot.callback_query_handler(func=lambda cb: cb.data.startswith('list_blocked'))
        def blocked_list_pages(cb):
            page_no = int(cb.data.replace('list_blocked', '', 1))
            pages_count, users = db.usr.get_blocked_page(page_no)
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
            markup.row(*pager_buttons('list_blocked', page_no, pages_count))
            bot.edit_message_text(
                s,
                parse_mode='HTML',
                reply_markup=markup,
                message_id=cb.message.message_id,
                chat_id=cb.from_user.id
            )
            bot.answer_callback_query(cb.id, strings.ans.done)

        # command for admin: lists all non-blocked users
        @bot.message_handler(func=lambda message: message.chat.id == my_id, commands=["viewuserlist"])
        def command_users(_):
            page_no = 1
            pages_count, users = db.usr.get_page(page_no)
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
            markup.row(*pager_buttons('list_users', page_no, pages_count))
            bot.send_message(
                my_id,
                s,
                parse_mode='HTML',
                reply_markup=markup
            )

        # handles inline keyboard buttons under the users list
        @bot.callback_query_handler(func=lambda cb: cb.data.startswith('list_users'))
        def user_list_pages(cb):
            page_no = int(cb.data.replace('list_users', '', 1))
            pages_count, users = db.usr.get_page(page_no)
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
            markup.row(*pager_buttons('list_users', page_no, pages_count))
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
            bot.forward_message(my_id, old_msg.chat.id, old_msg.message_id)

        # command for the admin to check his/her current status.
        # The dictionary.check_status() method simply reads the text in the availability.txt file
        @bot.message_handler(func=lambda message: message.chat.id == my_id, commands=["checkstatus"])
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
        @bot.message_handler(func=lambda message: message.chat.id != my_id, commands=["start"])
        def command_start_all(message):
            bot.send_message(
                message.chat.id,
                db.common.startmsg.format(name=message.from_user.first_name)
            )

        # Handle the messages which are not sent by the admin user(the one who is handling the bot)
        # Sends texts, audios, document etc to the admin
        @bot.message_handler(
            func=lambda message: message.chat.id != my_id,
            content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'voice', 'location', 'contact']
        )
        def handle_all(message):
            user = db.usr.get_by_id(message.from_user.id)  # get user from database
            if not user:  # If user is new
                user = model.User(_id=message.from_user.id, first_name=message.from_user.first_name)
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
                    my_id,
                    text,
                    parse_mode='HTML',
                    reply_markup=markup
                )

                if message.content_type != 'text':
                    bot.forward_message(my_id, message.chat.id, message.message_id)

                # check the status of the admin whether he's available or not
                if db.common.availability == 'unavailable':
                    # and notify user if unavailable
                    bot.send_message(message.chat.id, db.common.nonavailmsg)

        @bot.callback_query_handler(func=lambda cb: cb.data.startswith('reply_'))
        def reply_to(cb):
            db.common.replying_to = int(cb.data.replace('reply_', '', 1))
            bot.register_next_step_handler(cb.message, send_reply)
            bot.answer_callback_query(cb.id, strings.ans.reply)

        # handles admin's replies
        def send_reply(message):
            if db.common.replying_to:
                user_id = db.common.replying_to
            else:
                bot.send_message(my_id, strings.msg.noone_to_reply)
                return

            if message.content_type == 'text':
                bot.send_chat_action(user_id, action='typing')
                bot.send_message(user_id, message.text)
            elif message.content_type == "sticker":
                bot.send_chat_action(user_id, action='typing')
                bot.send_sticker(user_id, message.sticker.file_id)
            elif message.content_type == "photo":
                bot.send_chat_action(user_id, action='upload_photo')
                bot.send_photo(user_id, list(message.photo)[-1].file_id)
            elif message.content_type == "voice":
                bot.send_chat_action(user_id, action='record_audio')
                bot.send_voice(user_id, message.voice.file_id, duration=message.voice.duration)
            elif message.content_type == "document":
                bot.send_chat_action(user_id, action='upload_document')
                bot.send_document(user_id, data=message.document.file_id)
            elif message.content_type == "audio":
                bot.send_chat_action(user_id, action='upload_audio')
                bot.send_audio(
                    user_id,
                    performer=message.audio.performer,
                    audio=message.audio.file_id,
                    title=message.audio.title,
                    duration=message.audio.duration
                )
            elif message.content_type == "video":
                bot.send_chat_action(user_id, action='upload_video')
                bot.send_video(user_id, data=message.video.file_id, duration=message.video.duration)
            elif message.content_type == "location":
                # No Google Maps on my phone, so this code is untested, should work fine though
                bot.send_chat_action(user_id, action='find_location')
                bot.send_location(user_id, latitude=message.location.latitude, longitude=message.location.longitude)
            else:
                bot.send_message(my_id, strings.msg.invalid_content_type)

            message.with_user = user_id  # mark message as belonging to conversation with specified user
            db.msg.create(message)  # log message in db
            db.common.update_last_seen()

        username = bot.get_me().username
        print('Bot has Started\nPlease text the bot on: @{0}\nhttps://telegram.me/{0}'.format(username))
        bot.send_message(my_id, strings.msg.bot_started)


if __name__ == '__main__':
    bot = ProxyBot(config.token, config.my_id)
    bot.polling(none_stop=True)
