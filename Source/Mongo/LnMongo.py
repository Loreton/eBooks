#!/usr/bin/python3
# updated by ...: Loreto Notarantonio
# Version ......: 01-04-2020 17.46.41
import sys
import pymongo
# from pymongo import MongoClient
import time
import json, yaml

# https://www.w3schools.com/python/python_mongodb_create_collection.asp
# https://realpython.com/introduction-to-mongodb-and-python/
# http://docs.mongoengine.org/tutorial.html

# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.replace_one
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

        # --- check if record exists
        # es.: self._collection.count_documents({ '_id': record['_id'] }, limit = 1)
    def exists(self, filter):
        assert isinstance(filter, (dict))
        _exists = self._collection.count_documents(filter, limit = 1)
        if _exists:
            logger.info('record exists', filter)

        return _exists


    def checkFields(self, record):
        assert isinstance(record, (dict))
        _keys = record.keys()
        for _key in self._mandatory_keys:
            if _key not in _keys:
                logger.console("Rec: {index} - {_key} is missing".format(**locals()))
                record[_key] = ''

        """
            add '_id' field
            get the self._id_fields contents and join its words
        """
        _id = []
        for fld in self._id_fields:
            _id.extend(record[fld].split())
        record['_id'] = '_'.join(_id)


        return record

    '''
    def checkFields(self, data):
        assert isinstance(post_data, (dict))
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
    '''

    def insert(self, post_data, replace=False):
        assert isinstance(post_data, (list, dict))
        records = [post_data] if isinstance(post_data, dict) else post_data

        ret_value = {}
        # updated_records = result['inserted_ids']
        for index, record in enumerate(records):
            my_rec = self.checkFields(record)
            # --- check if record exists
            _filter = { '_id': my_rec['_id'] }
            if self.exists(_filter):
                if replace:
                    result = self._collection.replace_one(_filter, my_rec)
                    if result.modified_count == 1:
                        status = my_rec['_id']
                else:
                    result = 'ignored...'

            else:
                # import pdb
                # pdb.set_trace()
                result = self._collection.insert_one(my_rec)
                status  = result.inserted_id
                # if result.inserted_id==my_rec['_id']:
                #     status  = my_rec['_id']

            ret_value[index] = status

        # result = self._collection.insert_many(my_data)

        return ret_value


    def insert_xxx(self, post_data):
        assert isinstance(post_data, (dict))
        inp_data = [post_data] if isinstance(post_data, dict) else post_data

        my_data = self.checkFields(inp_data)
        result = self._collection.insert_many(my_data)

        return result







    def update(self, post_data):
        assert isinstance(post_data, (list, dict))
        inp_data = [post_data] if isinstance(post_data, dict) else post_data

        # result = db.test.update_one({'x': 1}, {'$inc': {'x': 3}})
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

