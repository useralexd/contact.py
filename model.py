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
    print(time)
    counter = int(str(oid)[-6:], 16)
    counter = int(str(counter)[-3:], 10)
    print(counter)
    time += counter
    print(time)
    s = base64.urlsafe_b64encode(time.to_bytes(6, 'big'))
    s = s[1:]
    s = s[::-1]
    return s

# adds Dictionaryable behavior and marks models which can be stored in db
class Model(types.Dictionaryable):
    def to_dic(self):
        d = {}
        for k, v in vars(self).items():
            if isinstance(v, Model):
                d[k] = v.to_dic()
            elif not str(k).startswith('_'):
                if str(k) == 'id':
                    k = '_id'
                d[k] = v
        return d


# Represents User and adds extra fields to telepot's class
class User(Model, types.User):
    def __init__(self, *args, **kwargs):
        if not args:
            args = (
                kwargs.get('_id') or kwargs.get('id'),
                kwargs['first_name'],
                kwargs.get('last_name'),
                kwargs.get('username'),
            )
        self.blocked = kwargs.get('blocked')
        super().__init__(*args)

    def update(self, data):
        assert self.id == str(data.id)
        self.first_name = data.first_name
        self.last_name = data.last_name
        self.username = data.username


# Represents message, add ObjectId
class Message(Model, types.Message):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = bson.ObjectId()

    def to_dic(self):
        d = dict()
        d['_id'] = self.id
        d['tg_id'] = self.message_id
        d['short_id'] = short_id(self.id)
        d['from_user'] = self.from_user.id
        if self.from_user.id == config.my_id:
            d['with'] = self.reply_to_message.from_user.id
        else:
            d['with'] = self.from_user.id

        if self.text:
            d['text'] = self.text
        else:
            d['text'] = 'Non text message: /m' + short_id(self.id)
        return d


# Just adds Dictionaryable to chat
class Chat(Model, types.Chat):
    pass


# Replaces classes in telepot.types
def replace_classes():
    types.User = User
    types.Message = Message
    types.Chat = Chat
