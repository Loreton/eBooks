#!/usr/bin/python3
# updated by ...: Loreto Notarantonio
# Version ......: 30-03-2020 16.37.04
import sys
import pymongo
# from pymongo import MongoClient
import time
import json, yaml

# https://stackoverflow.com/questions/30013763/can-i-have-a-mongodb-collection-as-a-class-attribute-in-python
class Collection():
    def __init__(self, db, collection_name):
        self.db = db
        self.collection_name = collection_name

    @property
    def client(self):
        if not hasattr(self.__class__, '_client'):
            self.__class__._client = MongoClient()

        return self.__class__._client

    @property
    def collection(self):
        if not hasattr(self, '_collection'):
            database = getattr(self.client, self.db)
            self._collection = getattr(database, self.collection_name)

        return self._collection