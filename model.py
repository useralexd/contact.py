from telebot import types as types
import bson

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


class Message(Model, types.Message):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = bson.ObjectId()


class Chat(Model, types.Chat):
    pass


def replace_models():
    types.User = User
    types.Message = Message
    types.Chat = Chat
