#!/usr/bin/python3
# updated by ...: Loreto Notarantonio
# Version ......: 27-03-2020 16.54.47

import pymongo
# from pymongo import MongoClient
import time
import json, yaml

# https://www.w3schools.com/python/python_mongodb_create_collection.asp
# https://realpython.com/introduction-to-mongodb-and-python/
# http://docs.mongoengine.org/tutorial.html
class LnMongo:

       # ***********************************************
        # * dictType can be:
        # *     a. OrderedDict
        # *     b. gv.Ln.LnDict
        # ***********************************************
    def __init__(self, logger):
        self._logger = logger

        # epoch time before API call
        start = time.time()

        # https://kb.objectrocket.com/mongo-db/check-if-a-mongodb-server-is-running-using-the-pymongo-python-driver-643
        try:
            # attempt to create a client instance of PyMongo driver
            client = pymongo.MongoClient(host = ["mongodb://localhost:27017/"], serverSelectionTimeoutMS=1500)
            # call the server_info() to verify that client instance is valid
            client.server_info() # will throw an exception

        except:
            print ("connection error. mongoDB server may be down!")
            print (time.time() - start)
            sys.exit(1)


