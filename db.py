from pymongo import MongoClient
from bson.objectid import ObjectId
from model import *
import config


class __DAO:
    def __init__(self, coll):
        self.coll = coll

    def get_all(self):
        raise NotImplementedError()

    def get_by_id(self, item_id):
        raise NotImplementedError()

    def update(self, item):
        raise NotImplementedError()

    def delete(self, item_id):
        raise NotImplementedError()

    def create(self, item):
        raise NotImplementedError()


class __UserDAO(__DAO):
    def get_by_id(self, item_id):
        db_rec = self.coll.find_one({'_id': int(item_id)})
        return User(**db_rec) if db_rec else None

    def get_all(self):
        return [User(**db_rec) for db_rec in self.coll.find({})]

    def update(self, item):
        self.coll.update_one({'_id': item.id}, {'$set': item.to_dict()}, upsert=True)

    def delete(self, item_id):
        self.coll.delete_one({'_id': item_id})

    def create(self, item):
        self.coll.insert_one(item.to_dict())


__db_client = MongoClient(config.db_auth)
__db = __db_client[config.db_name]

__usr_coll_name = 'usr'
if __usr_coll_name not in __db.collection_names():
    __db.create_collection(__usr_coll_name)
usr = __UserDAO(__db[__usr_coll_name])

