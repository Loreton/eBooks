#!/usr/bin/python3
# updated by ...: Loreto Notarantonio
# Version ......: 27-03-2020 17.36.34
import sys
import pymongo
# from pymongo import MongoClient
import time
import json, yaml

# https://www.w3schools.com/python/python_mongodb_create_collection.asp
# https://realpython.com/introduction-to-mongodb-and-python/
# http://docs.mongoengine.org/tutorial.html
class MongoDB:
# class LnMongo:

        # ***********************************************
        # * dictType can be:
        # *     a. OrderedDict
        # *     b. gv.Ln.LnDict
        # ***********************************************
    def __init__(self, dbname, logger):
        self._logger = logger
        self._dbname = dbname
        # self._conn = False

        # epoch time before API call
        start = time.time()

        # https://kb.objectrocket.com/mongo-db/check-if-a-mongodb-server-is-running-using-the-pymongo-python-driver-643
        try:
            # attempt to create a client instance of PyMongo driver
            client = pymongo.MongoClient(host = ["mongodb://localhost:27017/"], serverSelectionTimeoutMS=1500)
            # call the server_info() to verify that client instance is valid
            client.server_info() # will throw an exception
            # self._conn = True

        except:
            logger.error("Connection error. mongoDB server may be down!")
            logger.error("elapsed time", time.time() - start)
            sys.exit(1)


        self._mydb = client[dbname]


    ################################################
    #
    ################################################
    def openCollection(self, coll_name):
        return mydb[coll_name]       # create collection. A collection is not created until it gets content!


    ################################################
    #
    ################################################
    def deleteCollection(self, coll_name):
        if coll_name in self._mydb.list_collection_names():
            logger.info("Removing collection {coll_name}".format(**locals()))
            mycoll = mydb[MY_COLLECTION]       # create collection/Table In MongoDB, a collection is not created until it gets content!
            rCode = mycoll.drop()
            print("collection {coll_name} has been deleted RCode:{rCode}".format(**locals()))
