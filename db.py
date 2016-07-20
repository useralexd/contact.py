from pymongo import MongoClient
from bson.objectid import ObjectId
import model
import config


class __DAO:
    def __init__(self, coll, item_type):
        self.coll = coll
        assert issubclass(item_type, model.Model)
        self.type = item_type

    def get_by_id(self, item_id):
        db_rec = self.coll.find_one({'_id': str(item_id)})
        return self.type(**db_rec) if db_rec else None

    def get_all(self):
        return [self.type(**db_rec) for db_rec in self.coll.find({})]

    def update(self, item):
        self.coll.update_one({'_id': item.id}, {'$set': item.to_dic()}, upsert=True)

    def delete(self, item_id):
        self.coll.delete_one({'_id': item_id})

    def create(self, item):
        self.coll.insert_one(item.to_dic())


class __UserDAO(__DAO):
    def __init__(self, coll):
        super().__init__(coll, model.User)

    def get_blocked(self):
        return [self.type(**db_rec) for db_rec in self.coll.find({'blocked': True})]



class __MessageDAO(__DAO):
    def __init__(self, coll):
        super().__init__(coll, model.Message)


__db_client = MongoClient(config.db_auth)
__db = __db_client[config.db_name]


def __get_coll(coll_name):
    if coll_name not in __db.collection_names():
        __db.create_collection(coll_name)
    return __db[coll_name]

usr = __UserDAO(__get_coll('usr'))
msg = __MessageDAO(__get_coll('msg'))

