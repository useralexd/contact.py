from telebot import types as types
import bson
import base64

import config


def to_python(value):
    try:
        return bson.ObjectId(base64.urlsafe_b64decode(value))
    except (bson.errors.InvalidId, ValueError, TypeError):
        raise ValueError


def to_url(value):
    return base64.urlsafe_b64encode(value.binary)


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
                int(kwargs.get('_id') or kwargs.get('id')),
                kwargs['first_name'],
                kwargs.get('last_name'),
                kwargs.get('username'),
            )
        self.blocked = kwargs.get('blocked') or False
        super().__init__(*args)


# Represents message, add ObjectId
class Message(Model, types.Message):
    def __init__(self, *args, **kwargs):
        if args:
            self.id = bson.ObjectId()
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
            self.text = kwargs['text']

    def to_dic(self):
        d = dict()
        d['_id'] = self.id
        d['short_id'] = short_id(self.id)

        d['message_id'] = self.message_id
        d['from_user'] = self.from_user.to_dic()
        d['date'] = self.date
        d['chat'] = self.chat.to_dic()
        d['content_type'] = self.content_type

        if self.text:
            d['text'] = self.text
        else:
            d['text'] = 'Non text message: /msg' + d['short_id']
        return d

    def __format__(self, format_spec):
        return """{user}: {text}""".format(user=self.from_user.first_name, text=self.text)


class Chat(Model, types.Chat):
    def __init__(self, *args, **kwargs):
        if not args:
            args = (
                int(kwargs.get('_id') or kwargs.get('id')),
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
                text += self.title
            elif self.first_name:
                text += self.first_name
            else:
                text += '<code>_unnamed_</code>'

            if self.username:
                text += '(@' + self.username + ')'
        elif format_spec == 'btn':
            text = '[' + self.type + ']'
            if self.title:
                text += self.title
            elif self.first_name:
                text += self.first_name
            else:
                text += '_unnamed_'
        else:
            text = ''
        return text

# Replaces classes in telebot.types
def replace_classes():
    types.User = User
    types.Message = Message
    types.Chat = Chat

replace_classes()
