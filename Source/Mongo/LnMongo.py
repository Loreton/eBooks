#!/usr/bin/python3
# updated by ...: Loreto Notarantonio
# Version ......: 31-03-2020 10.20.38
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
    def __init__(self, db_name, myLogger, server_name='127.0.0.1', server_port='27017'):
        global logger
        logger = myLogger
        self._db_name = db_name
        self._client  = self.dbConnect(server_name, server_port)
        self._db      = self._client[db_name] # create DB In MongoDB, a database is not created until it gets content




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
            logger.console("Connection error. mongoDB server may be down!")
            logger.console("elapsed time", time.time() - start)
            sys.exit(1)

        logger.console ('CLIENT:', client)
        return client



    ################################################
    #
    ################################################
    def openCollection(self, coll_name):
        return self._db[coll_name]       # create collection. A collection is not created until it gets content!


    ################################################
    #
    ################################################
    def deleteCollection(self, coll_name):
        if coll_name in self._db.list_collection_names():
            logger.info("Removing collection {coll_name}".format(**locals()))
            mycoll = self._db[coll_name]       # create collection/Table In MongoDB, a collection is not created until it gets content!
            rCode = mycoll.drop()
            print("collection {coll_name} has been deleted RCode:{rCode}".format(**locals()))


class Mongo2DB:
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

        logger.console ('CLIENT:', client)
        return client



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


class LnCollection:

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