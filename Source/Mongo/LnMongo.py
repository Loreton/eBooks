#!/usr/bin/python3
# updated by ...: Loreto Notarantonio
# Version ......: 31-03-2020 15.36.59
import sys
import pymongo
# from pymongo import MongoClient
import time
import json, yaml

# https://www.w3schools.com/python/python_mongodb_create_collection.asp
# https://realpython.com/introduction-to-mongodb-and-python/
# http://docs.mongoengine.org/tutorial.html

class MongoDB:
        # ***********************************************
        # ***********************************************
    def __init__(self, db_name, collection_name, myLogger, server_name='127.0.0.1', server_port='27017'):
        global logger
        logger = myLogger
        self._db_name = db_name
        self._collection_name = collection_name

        self._client  = self.dbConnect(server_name, server_port)
        self._db      = self._client[db_name] # create DB In MongoDB, a database is not created until it gets content
        self._collection = self._db[collection_name] # create collection. A collection is not created until it gets content!



    ################################################
    #
    ################################################
    def dbConnect(self, server_name, server_port):
        # epoch time before API call
        start = time.time()
        # db = None

        try:
            # attempt to create a client instance of PyMongo driver
            DBserver="mongodb://{server_name}:{server_port}/".format(**locals())
            client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=1500)
            # call the server_info() to verify that client instance is valid
            client.server_info() # will throw an exception

        except:
            logger.error("Connection error. mongoDB server may be down!")
            logger.error("elapsed time", time.time() - start)
            logger.console("Connection error. mongoDB server may be down!")
            sys.exit(1)

        logger.info ('CLIENT:', client)
        return client


    def setFields(self, fields):
        self._mandatory_keys = fields

    def setIdFields(self, fields):
        self._id_fields = fields


    def checkFields(self, data):
        for index, record in enumerate(data):
            _keys = record.keys()
            for _key in self._mandatory_keys:
                if _key not in _keys:
                    logger.console("Rec: {index} - {_key} is missing".format(**locals()))
                    record[_key] = ''

            # --- add '_id' field
            _id = []
            for fld in self._id_fields:
                _id.extend(record[fld].split())
            record['_id'] = '_'.join(_id)
            if self._collection.count_documents({ '_id': record['_id'] }, limit = 1):
                print('record exixsts')
                sys.exit(1)

        return data

    def insert(self, post_data):
        assert isinstance(post_data, (list, dict))
        inp_data = [post_data] if isinstance(post_data, dict) else post_data

        my_data = self.checkFields(inp_data)
        result = self._collection.insert_many(my_data)

        return result



    ################################################
    #
    ################################################
    # def fields(self):
    #     title = StringField(max_length=120, required=True)
    #     author = ReferenceField(User)
    #     tags = ListField(StringField(max_length=30))
    #     comments = ListField(EmbeddedDocumentField(Comment))


    ################################################
    #
    ################################################
    @property
    def collection(self):
        if not hasattr(self, '_collection'):
            database = getattr(self._client, self._db)
            self._collection = getattr(database, self._collection_name)

        return self._collection

    ################################################
    #
    ################################################
    @property
    def client(self):
        if not hasattr(self.__class__, '_client'):
            self.__class__._client = MongoClient()

        return self.__class__._client

    # def openCollection(self, coll_name):
    #     return mydb[coll_name]       # create collection. A collection is not created until it gets content!


    ################################################
    #
    ################################################
    def deleteCollection(self, coll_name):
        if coll_name in self._mydb.list_collection_names():
            logger.info("Removing collection {coll_name}".format(**locals()))
            mycoll = mydb[MY_COLLECTION]       # create collection/Table In MongoDB, a collection is not created until it gets content!
            rCode = mycoll.drop()
            print("collection {coll_name} has been deleted RCode:{rCode}".format(**locals()))

