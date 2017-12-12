from flask import Flask, request
import telebot

import proxy_bot
import config

app = Flask(__name__)


class WebhookProxyBot(proxy_bot.ProxyBot):
    def __init__(self, token, master_id, server, baseurl, cert=None):
        path = 'proxybot/' + token
        super().__init__(token, master_id)

        @server.route('/' + path, methods=['POST'])
        def webhook_updates():
            update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
            self.process_new_updates([update])
            return 'OK'

        if cert:
            cert = open(cert, 'rb')
        self.set_webhook(
            url=baseurl + path,
            certificate=cert
        )
        print('webhook set on ' + baseurl + path)


bot = WebhookProxyBot(
    config.token,
    config.my_id,
    app,
    config.baseurl,
    config.ssl_context[0]
)

if __name__ == '__main__':
    app.run(
        host=config.host,
        port=config.port,
        ssl_context=config.ssl_context,
    )
