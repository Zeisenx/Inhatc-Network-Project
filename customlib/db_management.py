from pymongo import MongoClient
from content import mongodb_info


class InhatcItemDB:
    def __init__(self):
        self.__db = MongoClient(mongodb_info.conn_str)['items']

    def find_members(self):
        return self.__db.collection_names()

    def add(self, chat_id, **kwargs):
        return self.__db[chat_id].insert_one(kwargs)

    def remove(self, chat_id, key):
        self.__db[chat_id].remove({"_id": key})

    def find_all(self, chat_id):
        return list(self.__db[chat_id].find())
