from telebot import types as types
import bson


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


# Just adds Dictionaryable to chat
class Chat(Model, types.Chat):
    pass


# Replaces classes in telepot.types
def replace_classes():
    types.User = User
    types.Message = Message
    types.Chat = Chat
