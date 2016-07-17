from telebot import types as types


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
    def __init__(self, **kwargs):
        id = kwargs.get('_id') or kwargs.get('id')
        first_name = kwargs['first_name']
        last_name = kwargs.get('last_name')
        username = kwargs.get('username')
        self.blocked = kwargs.get('blocked')
        super().__init__(id, first_name, last_name, username)

    def update(self, data):
        assert self.id == str(data.id)
        self.first_name = data.first_name
        self.last_name = data.last_name
        self.username = data.username
