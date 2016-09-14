#!/usr/bin/env python3

import telebot
from telebot import types
import logging

import config
import proxy_bot

telebot.logger.setLevel(logging.WARNING)


class MasterBot(telebot.TeleBot):
    def __init__(self, token, sub_bot):
        super().__init__(token)
        bot = self
        self.sub_bot = sub_bot

        @bot.message_handler(commands=['start', 'help'])
        def start(message):
            bot.reply_to(message, '''\
Semd me api_token and I will spawn an proxy_bot for you.
More info at https://github.com/p-hash/proxybot''')

        @bot.message_handler()
        def check_token(message):
            if message.chat.type != 'private':
                return
            new_bot_token = message.text
            new_bot_owner = message.from_user.id

            try:
                new_bot = sub_bot(new_bot_token, new_bot_owner)
            except telebot.apihelper.ApiException:
                bot.reply_to(message, "An error occured: the token is invalid or you haven't started the bot yet.")
                return

            if new_bot:
                self.run_bot(new_bot)

        username = bot.get_me().username
        print('MasterBot has Started\nPlease text the bot on: @{0}\nhttps://telegram.me/{0}'.format(username))

    def run_bot(self, bot):
        bot.polling(none_stop=True)

if __name__ == '__main__':
    bot = MasterBot(config.token, proxy_bot.ProxyBot)
    bot.polling(none_stop=True)
