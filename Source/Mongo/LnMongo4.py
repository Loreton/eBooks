#!/usr/bin/python3
# updated by ...: Loreto Notarantonio
# Version ......: 30-03-2020 16.39.25
import sys
import pymongo
# from pymongo import MongoClient
import time
import json, yaml

import pymongo
class mongoresultDAO(object):

       def __init__(self, database, collection):
               self.db = database
               self.dbcollection = collection
               self.connect()

       def find_names(self, model, query, param):
               #print query
               #print param
               mongor1 = self.dbcollection.find(query, param)
               #print mongor1
               return mongor1

       def update_collection(self,jsonObj):
               self.dbcollection.insert(jsonObj,check_keys=False)

      def connect(self):
               client = pymongo.MongoClient("localhost", 27017)
               db = client[self.db]
               coll_obj = db[self.dbcollection]
               return coll_obj