from telebot import types as types
import bson
import base64

import html_helper


def short_id(value):
    oid = bson.ObjectId(str(value))
    time = int(oid.generation_time.timestamp()) * 1000
    counter = int(str(oid)[-6:], 16)
    counter = int(str(counter)[-3:], 10)
    time += counter
    s = base64.urlsafe_b64encode(time.to_bytes(6, 'big'))
    s = s[1:]
    s = s[::-1]
    return s.decode('ascii')


# adds Dictionaryable behavior and marks models which can be stored in db
class Model(types.Dictionaryable):
    def to_dic(self):
        d = {}
        for k, v in vars(self).items():
            if isinstance(v, Model):
                d[k] = v.to_dic()
            elif not str(k).startswith('_'):
                d[k] = v
        return d


# Represents User and adds extra fields to telepot's class
class User(Model, types.User):
    def __init__(self, *args, **kwargs):
        if not args:
            args = (
                int(kwargs['id']),
                kwargs['first_name'],
                kwargs.get('last_name'),
                kwargs.get('username'),
            )
        super().__init__(*args)


# Represents message, add ObjectId
class Message(Model, types.Message):
    def __init__(self, *args, **kwargs):
        if args:
            self.id = bson.ObjectId()
            self.short_id = short_id(self.id)
            self.html = None
            super().__init__(*args)
        else:
            super().__init__(
                kwargs['message_id'],
                User(**kwargs['from_user']),
                kwargs['date'],
                Chat(**kwargs['chat']),
                kwargs['content_type'],
                options={}
            )
            self.id = kwargs['_id']
            self.short_id = kwargs['short_id']
            self.text = kwargs.get('text')
            self.html = kwargs.get('html')
            if 'entities' in kwargs:
                self.entities = [MessageEntity(**ent) for ent in kwargs.get('entities')]

    def to_dic(self):
        d = dict()
        d['_id'] = self.id
        d['short_id'] = self.short_id

        d['message_id'] = self.message_id
        d['from_user'] = self.from_user.to_dic()
        d['date'] = self.date
        d['chat'] = self.chat.to_dic()
        d['content_type'] = self.content_type
        if self.entities:
            d['entities'] = [entity.to_dic() for entity in self.entities]

        d['text'] = self.text
        d['html'] = self.html

        return d

    def __format__(self, format_spec):
        if not self.html:
            self.html = html_helper.to_html(self)
        return """{user}: {text}""".format(
            user=html_helper.escape_html(self.from_user.first_name),
            text=self.html
        )

    @property
    def html_form(self):
        return html_helper.entities_to_html(self.text, self.entities)

    @property
    def md_form(self):
        return html_helper.entities_to_md(self.text, self.entities)

    # not used for now
    def clear_entities(self):
        for entity in self.entities:
            if entity.type in ['mention', 'hashtag', 'bot_command', 'url', 'email', 'text_mention']:
                self.entities.remove(entity)


class Chat(Model, types.Chat):
    def __init__(self, *args, **kwargs):
        if not args:
            args = (
                int(kwargs['id']),
                kwargs['type'],
                kwargs.get('title'),
                kwargs.get('username'),
                kwargs.get('first_name'),
                kwargs.get('last_name'),
            )
        self.blocked = kwargs.get('blocked') or False
        super().__init__(*args)

    def update(self, data):
        self.last_name = data.last_name
        self.first_name = data.first_name
        self.username = data.username
        self.title = data.title

    def __format__(self, format_spec):
        if format_spec == 'html':
            text = '<code>[' + self.type + '] </code>'
            if self.title:
                text += html_helper.escape_html(self.title)
            elif self.first_name:
                text += html_helper.escape_html(self.first_name)
            else:
                text += '<code>_unnamed_</code>'

            if self.username:
                text += ' (@' + self.username + ')'
        elif format_spec == 'btn':
            text = '[' + self.type + ']'
            if self.title:
                text += self.title
            elif self.first_name:
                text += self.first_name
            else:
                text += '_unnamed_'
        elif format_spec == 'full':
            text = '<b>Chat</b>\n<code>Id:</code> {id}\n<code>Type:</code> {type}'
            if self.title:
                text += '\n<code>Title:</code> {title}'
            if self.username:
                text += '\n<code>Username:</code> @{username}'
            if self.first_name:
                text += '\n<code>First Name:</code> {first_name}'
            if self.last_name:
                text += '\n<code>Last Name:</code> {last_name}'
            text += '\n<code>Is blocked?</code> <i>{blocked}</i>'
            text = text.format(
                id=self.id,
                type=self.type,
                title=html_helper.escape_html(self.title),
                username=self.username,
                first_name=html_helper.escape_html(self.first_name),
                last_name=html_helper.escape_html(self.last_name),
                blocked=self.blocked
            )
        else:
            text = ''
        return text


class MessageEntity(Model, types.MessageEntity):
    def __init__(self, *args, **kwargs):
        if not args:
            args = (
                kwargs['type'],
                int(kwargs['offset']),
                int(kwargs['length']),
                kwargs.get('url')
            )
        super().__init__(*args)


class Bot(Model):
    def __init__(self, bot=None, **kwargs):
        if bot:
            bot_user = bot.get_me()
            self.id = bot_user.id
            self.username = bot_user.username
            self.first_name = bot_user.first_name
            self.master_id = bot.master_id
            self.token = bot.token
        else:
            self.id = kwargs['id']
            self.username = kwargs['username']
            self.first_name = kwargs['first_name']
            self.master_id = kwargs['master_id']
            self.token = kwargs['token']


# Replaces classes in telebot.types
def replace_classes():
    types.User = User
    types.Message = Message
    types.Chat = Chat
    types.MessageEntity = MessageEntity

replace_classes()
