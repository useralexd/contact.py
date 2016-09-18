from flask import Flask, request
import telebot

import proxy_bot
import db_helper
import config
import model


class WebhookMasterBot(telebot.TeleBot):
    def __init__(self, token, server, baseurl, cert):
        path = 'masterbot/' + token
        super().__init__(token)
        bot = self
        bot.remove_webhook()
        db = db_helper.MasterBotDB()

        sub_bots = dict()
        for b in db.bots.get_all():
            sub_bot = proxy_bot.ProxyBot(b.token, b.master_id)
            sub_bot.set_webhook(
                url=baseurl + 'proxybot/' + b.token,
                certificate=open(cert, 'rb')
            )
            db.bots.update(model.Bot(sub_bot))
            sub_bots[b.token] = sub_bot

        @server.route('/' + path, methods=['POST'])
        def webhook_updates():
            update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
            self.process_new_updates([update])
            return 'OK'

        @server.route('/proxybot/<sub_token>', methods=['POST'])
        def sub_bot_updates(sub_token):
            update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
            sub_bots[sub_token].process_new_updates([update])
            return 'OK'

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

            if db.bots.get_by_master(new_bot_owner):
                bot.reply_to(message, "You already have one proxybot. Contact @phash_bot for details.")
                return

            try:
                new_bot = proxy_bot.ProxyBot(new_bot_token, new_bot_owner)
            except telebot.apihelper.ApiException:
                bot.reply_to(message, "An error occured: the token is invalid or you haven't started your bot yet.")
                return

            if new_bot:
                db.bots.create(model.Bot(new_bot))
                new_bot.set_webhook(
                    url=baseurl + '/proxybot/' + new_bot_token,
                    certificate=open(cert, 'rb')
                )

        self.set_webhook(
            url=baseurl + path,
            certificate=open(cert, 'rb')
        )
        print('webhook set on ' + baseurl + path)


if __name__ == '__main__':
    server = Flask('masterbot')

    bot = WebhookMasterBot(
        config.token,
        server,
        config.baseurl,
        config.ssl_context[0]
    )

    server.run(
        host=config.host,
        port=config.port,
        ssl_context=config.ssl_context,
    )
