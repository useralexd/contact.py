from pymongo import MongoClient
from time import time

import model
import config


class DAO:
    def __init__(self, coll, item_type, bot_id=None):
        self.coll = coll
        assert issubclass(item_type, model.Model)
        self.type = item_type
        self.bot_id = bot_id

    def get_by_id(self, item_id):
        query = {'id': item_id}
        if self.bot_id:
            query['bot_id'] = self.bot_id
        db_rec = self.coll.find_one(query)
        return self.type(**db_rec) if db_rec else None

    def get_all(self):
        query = {}
        if self.bot_id:
            query['bot_id'] = self.bot_id
        return [self.type(**db_rec) for db_rec in self.coll.find(query)]

    def update(self, item):
        query = {'id': item.id}
        if self.bot_id:
            query['bot_id'] = self.bot_id
        self.coll.update_one(query, {'$set': item.to_dic()}, upsert=True)

    def delete(self, item_id):
        query = {'id': item_id}
        if self.bot_id:
            query['bot_id'] = self.bot_id
        self.coll.delete_one(query)

    def create(self, item):
        dic = item.to_dic()
        if self.bot_id:
            dic['bot_id'] = self.bot_id
        self.coll.insert_one(dic)

    def _get_page(self, page_no=1, page_size=5, query=None):
        if query is None:
            query = {}
        if self.bot_id:
            query['bot_id'] = self.bot_id
        cursor = self.coll.find(query).sort('_id', 1)
        count = cursor.count()
        if count < 1:
            return 0, None
        pages_count = count // page_size
        if count % page_size:
            pages_count += 1
        return (
            pages_count,
            [
                self.type(**db_rec)
                for db_rec in
                cursor.skip(page_size * (page_no - 1)).limit(page_size)
            ]
        )


class ChatDAO(DAO):
    def __init__(self, coll, bot_id):
        super().__init__(coll, model.Chat, bot_id)

    def get_page(self, list_type=None, page_no=1, page_size=5):
        if list_type == 'user':
            return self.get_private_page(page_no, page_size)
        elif list_type == 'group':
            return self.get_groups_page(page_no, page_size)
        elif list_type == 'channel':
            return self.get_channels_page(page_no, page_size)
        elif list_type == 'blocked':
            return self.get_blocked_page(page_no, page_size)
        else:
            return self._get_page(page_no, page_size)

    def get_private_page(self, page_no=1, page_size=5):
        return self._get_page(page_no, page_size, {'type': 'private', 'blocked': False})

    def get_groups_page(self, page_no=1, page_size=5):
        query = {'$or': [{'type': 'group'}, {'type': 'supergroup'}], 'blocked': False}
        return self._get_page(page_no, page_size, query)

    def get_channels_page(self, page_no=1, page_size=5):
        return self._get_page(page_no, page_size, {'type': 'channel', 'blocked': False})

    def get_blocked_page(self, page_no=1, page_size=5):
        return self._get_page(page_no, page_size, {'blocked': True})


class MessageDAO(DAO):
    def __init__(self, coll, bot_id):
        super().__init__(coll, model.Message, bot_id)

    def get_chat_page(self, chat_id, page_no=0, page_size=4):
        cursor = self.coll.find({'bot_id': self.bot_id, 'chat.id': chat_id}).sort('_id', 1)
        count = cursor.count()
        if count < 1:
            return 0, None
        pages_count = count // page_size + (1 if count % page_size else 0)
        if page_no == 0:
            page_no = pages_count
        return (
            pages_count,
            [
                self.type(**db_rec)
                for db_rec in
                cursor.skip(page_size * (page_no - 1)).limit(page_size)
            ]
        )

    def get_by_shortid(self, shortid):
        db_rec = self.coll.find_one({'bot_id': self.bot_id, 'short_id': shortid})
        return self.type(**db_rec) if db_rec else None


class CommonData:
    def __init__(self, coll, bot_id):
        self.coll = coll
        self.data = coll.find_one({'bot_id': bot_id})
        if self.data is None:
            self.data = {
                'messages': dict(),
                'bot_id': bot_id,
            }
            result = self.coll.insert_one(self.data)
            self.data['_id'] = result.inserted_id

        self._replying_to = None
        self._replying_to_expiration = config.replying_expiration
        self._availability_expiration = config.availability_expiration
        self._last_seen = time() - self._availability_expiration  # default to unavailable
        self._replying_to_update = self._last_seen

    @property
    def availability(self):
        if time() - self._last_seen > self._availability_expiration:
            return 'unavailable'
        else:
            return 'available'

    @property
    def messages(self):
        if not self.data.get('messages'):
            self.data['messages'] = dict()
        return self.data.get('messages')

    def save(self):
        self.coll.update_one({'_id': self.data['_id']}, {'$set': self.data})

    @property
    def blockmsg(self):
        return self.data['messages'].get('block') or ''

    @property
    def nonavailmsg(self):
        return self.data['messages'].get('unavailable') or ''

    @property
    def startmsg(self):
        return self.data['messages'].get('start')

    @property
    def replying_to(self):
        if time() - self._replying_to_update > self._replying_to_expiration:  # if admin wasn't here for a quite long time
            self._replying_to = None  # ignore last replying_to
        return self._replying_to

    @replying_to.setter
    def replying_to(self, value):
        self._replying_to = value
        self._replying_to_update = time()

    def update_last_seen(self):
        self._last_seen = time()

    @property
    def last_seen(self):
        return self._last_seen

    @property
    def markdown(self):
        if 'markdown' in self.data:
            return self.data['markdown']
        else:
            return True

    @markdown.setter
    def markdown(self, value):
        value = bool(value)
        self.data['markdown'] = value
        self.save()

    state = 'none'
    prev_msg = None


class BotsDAO(DAO):
    def __init__(self, coll):
        super().__init__(coll, model.Bot)

    def get_by_master(self, master_id):
        db_rec = self.coll.find_one({'master_id': master_id})
        return self.type(**db_rec) if db_rec else None

db_client = MongoClient(config.db_auth)
db = db_client[config.db_name]


def get_coll(coll_name):
    if coll_name not in db.collection_names():
        db.create_collection(coll_name)
    return db[coll_name]


class DB:
    def __init__(self, bot_id):
        self.chat = ChatDAO(get_coll('chat'), bot_id)
        self.msg = MessageDAO(get_coll('msg'), bot_id)
        self.common = CommonData(get_coll('common'), bot_id)


class MasterBotDB:
    def __init__(self):
        self.bots = BotsDAO(get_coll('bots'))
