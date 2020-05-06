#!/usr/bin/python3
#
# updated by ...: Loreto Notarantonio
# Version ......: 05-05-2020 10.29.45
#
import sys
import pymongo
# from pymongo import MongoClient
import time
import json, yaml
from dotmap import DotMap
# from Source.LnLib.LnDotMapp import DotMap
from Source import LnClass
# class LnClass():
#     pass

# https://www.w3schools.com/python/python_mongodb_create_collection.asp
# https://realpython.com/introduction-to-mongodb-and-python/
# http://docs.mongoengine.org/tutorial.html
# https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.replace_one



class MongoCollection:
    # DBs=DotMap(_dynamic=False) # Global var per gestire più DBases
    DBs={} # Global var per gestire più DBases
        # ***********************************************
        # ***********************************************
    def __init__(self, db_name, collection_name, myLogger, server_name='127.0.0.1', server_port='27017'):
        global logger
        logger = myLogger
        self._db_name = db_name
        self._collection_name = collection_name
        self._client  = self._dbConnect(db_name, server_name, server_port)
        self._db      = self._client[db_name] # create DB In MongoDB, a database is not created until it gets content
        self._collection = self._db[collection_name] # create collection. A collection is not created until it gets content!

        self._from = 0
        self._range = 1
        self._query = {}

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

    ################################################
    #
    ################################################
    def _dbConnect(self, db_name, server_name, server_port):
        _DBs = MongoCollection.DBs # accedi alla variabile globale di classe
        if not db_name in _DBs.keys():
            start = time.time()

            try:
                # attempt to create a client instance of PyMongo driver
                DBserver="mongodb://{server_name}:{server_port}/".format(**locals())
                client = pymongo.MongoClient(DBserver, serverSelectionTimeoutMS=1500)

                # call the server_info() to verify that client instance is valid
                client.server_info() # will throw an exception

            except:
                logger.error("Connection error. mongoDB server may be down!")
                logger.error("elapsed time", time.time() - start)
                logger.console("Connection error. mongoDB server may be down!")
                sys.exit(1)

            # logger.info ('CLIENT:', client)

            _DBs[db_name] = {}
            _DBs[db_name]['client'] = client
            _DBs[db_name]['db']     = client[db_name]

        return _DBs[db_name]['client']




    def setFields(self, fields):
        self._fields = fields

    def setIdFields(self, fields):
        self._id_fields = fields

    @property
    def fields(self):
        return self._fields

    @property
    def idFields(self, fields):
        return self._id_fields


    ############################################################
    # --- check if record exists
    # --- if exists return existing record
    # es.: self._collection.count_documents({ '_id': record['_id'] }, limit = 1)
    ############################################################
    def exists(self, rec):
        _exists = self._collection.count_documents(rec['_filter'], limit = 1)
        if _exists:
            logger.info('record exists', rec['_filter'])
            _rec = self.get_record(rec['_filter'])
        else:
            logger.error('record NOT found', rec['_filter'])
            _rec={}


        return _rec




        ############################################################
        # https://docs.python.org/3/library/stdtypes.html#frozenset.symmetric_difference
        # diff_a = set(record['keys']()).difference(set(self._fields))
        # diff_b = set(self._fields).difference(set(record['keys']()))
        ############################################################
    def _checkFields(self, record):
        assert isinstance(record, (dict))
        diff = set(record.keys()).symmetric_difference(set(self._fields))
        if diff:
            print("     {diff} field(s) is(are) not included in both structure fields:".format(**locals()))
            print('     structure fields:')
            for index, field in enumerate(sorted(self._fields), start=1):
                print('     {index} - {field}'.format(**locals()))
            print()
            print('     record  fields:')
            for index, field in enumerate(sorted(record.keys()), start=1):
                print('     {index} - {field}'.format(**locals()))
            logger.critical('Please provide a right fields')

        return record


    ####################################################
    # - Calcola ID ed imposta i seguenti campi nel record:
    # -  _id:     IDvalue
    # -  filter: {'_id': IDvalue}
    ####################################################
    def set_id(self, rec):
        # import pdb;pdb.set_trace()

        _id = []
        for fld in self._id_fields:
            words = rec[fld].split()
            for word in words:
                word=[ c.strip() for c in word if c.isalnum()]
                _id.append(''.join(word))

        _id = ' '.join(_id).split() #  remove empty elements
        IDvalue ='_'.join(_id)
        if not '_id' in rec:
            rec['_id'] = IDvalue

        if not '_filter' in rec:
            rec['_filter'] = {'_id': IDvalue}



    ####################################################
    # -
    ####################################################
    def get_record(self, filter):
        book = self._collection.find_one(filter) # get current record
        return book


    ############################################################
    # per DB molto grandi ed evitare problemi di CursorNotFound
    # return cursor
    ############################################################
    def get_range(self, skip, limit):
        # cursor = self._ePubs._collection.find({}, no_cursor_timeout=True)
        logger.info('reading records from', skip, 'to:', limit)
        return self._collection.find({}).skip(skip).limit(limit)


    ############################################################
    # per DB molto grandi ed evitare problemi di CursorNotFound
    # return cursor
    # cursor = self._ePubs._collection.find({}, no_cursor_timeout=True)
    ############################################################
    def get_next(self, nrecs=None, query=None):
        _my_query = self._query if not query else query
        # logger.info('query', str(_my_query), console=False)

        if not nrecs: nrecs=self._range
        logger.info('searching records', 'query', str(_my_query), self._from, 'for:', nrecs, console=False)
        print('searching records from:{self._from} for:{nrecs}'.format(**locals()))
        cursor = self._collection.find(_my_query, { "_id": 1 }).skip(self._from).limit(nrecs)
        # cursor = self._collection.find(_my_query).skip(self._from).limit(nrecs)
        records=list(cursor) # cursor si azzera al primo utilizzo
        self._from += nrecs # prepare for next
        return records

    ############################################################
    # per DB molto grandi ed evitare problemi di CursorNotFound
    # return cursor
    ############################################################
    def set_query(self, query={} ):
        self._query = query

    def count(self, query={} ):
        _my_query = self._query if not query else query
        # logger.info('query', str(_my_query), console=True)
        nrecs = self._collection.find(_my_query).count()
        return nrecs

    ############################################################
    # per DB molto grandi ed evitare problemi di CursorNotFound
    # return cursor
    ############################################################
    def set_range(self, start=1, range=1):
        if start>0: start -= 1 # parte da 0
        self._from = start
        self._range = range
        return self._from







    ####################################################
    # -
    ####################################################
    def insert_one(self, record, replace=False):
        """ insert document record into collection
            return:
                ['replaced', _filter ]
                ['exists', _filter ]
                ['inserted', _filter]
        """
        # assert isinstance(record, (dict))

        self._checkFields(record)

        curr_rec = self.exists(rec=record)
        if curr_rec:
            if replace:
                result = self._collection.replace_one(record['_filter'], record) # non riconosce bene DotMap
                if result.modified_count == 1:
                    status = ['replaced', record['_filter'] ]
            else:
                status = ['exists', record['_filter'] ]

        else:
            result = self._collection.insert_one(record) # non riconosce bene DotMap
            status  = ['inserted', record['_filter']]


        return status

    # ################################################
    # - https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.update_one
    #   myquery = { "address": "Valley 345" }
    #   newvalues = { "$set": { "address": "Canyon 123" } }
    #   mycol.update_one(myquery, newvalues)
    #   db.getCollection('ePubs').update_many({'indexed': true}, {'$inc': {'indexed': false}})
    # ################################################
    def updateField_many(self, filter, update):
        return self._collection.update_many(filter, update)


    # ################################################
    # - https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.update_one
    #   myquery = { "address": "Valley 345" }
    #   newvalues = { "$set": { "address": "Canyon 123" } }
    #   mycol.update_one(myquery, newvalues)
    # ################################################
    def updateField(self, rec, fld_name, create=False):

        # https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.find_one
        _base_msg = 'Updating field {fld_name} in record {0}'.format(rec['_filter'], **locals())
        logger.console(self._collection_name, 'Updating field', fld_name, 'in record', rec['_filter'])

        fld_new_value = rec[fld_name]
        cur_rec=self._collection.find_one(rec['_filter']) # get current record
        if cur_rec:
            cur_value = cur_rec[fld_name]
            if isinstance(cur_value, (list, tuple)): # if it's a list
                _val = cur_value[:]
                _val.extend(fld_new_value)
                _val = list(set(_val)) # remove duplicates ... anche list( dict.fromkeys(_val)
                # _val = list( dict.fromkeys(_val) ) # remove duplicates ... anche list(set(_val))
            else:
                _val = fld_new_value

            if _val == cur_value:
                result = LnClass()
                result.matched_count = 1
                result.modified_count = 0
                logger.debug1(_base_msg, ' matching, nothig to do.')

            else:
                logger.info(_base_msg, ' ... updating')
                upd_cmd = { "$set": {fld_name: _val } }
                result=self._collection.update_one(rec['_filter'], upd_cmd)
                logger.debug1('   matched', result.matched_count)
                logger.debug1('   updated', result.modified_count)

        elif create:
            logger.info(_base_msg, ' record not found. Creating it.')
            result = self.insert_one(rec)

        return result



    # https://docs.mongodb.com/manual/reference/operator/query/regex/
    def searchWord(self, search_text):
        # db.articles.find( { $text: { $search: "coffee" } } )
        return self._collection.find({"$text": {"$search": search_text}})


    def search(self, field_name, regex, ignore_case=False):
        '''
        https://docs.mongodb.com/manual/reference/operator/query/regex/
            use $regex to find docs that start with case-sensitive "obje"
            The .* included at the end of the "$regex" key’s value
            acts as a wildcard along with the string match.
              query = { "field": { "$regex": 'obje.*' } }
              docs = col.count_documents( query )

            For an exact string match, just put the
            specified string between the ^ and $ characters:
                query = { "field": { "$regex": '^ObjectRocket 2$' } }
                docs = col.count_documents( query )

            In the following example, we’ll create an "$options" key,
            in addition to our "$regex", and we’ll set the value of
            this key to "i" to make the query case-insensitive
                query = { "field": { "$regex": 'oBjEcT', "$options" :'i' } }
                docs = col.count_documents( query )
        '''
        _ic='i' if ignore_case else ''
        query = {
            field_name: {
            "$regex": regex,
            "$options" : _ic # case-insensitive
            }
        }
        logger.info('my_query', query)
        # result = self._collection.find(query).limit(10)
        result = self._collection.find(query)
        # logger.info('    record found', result.count())
        return result



    ################################################
    #
    ################################################
    def deleteCollection(self, coll_name):
        if coll_name in self._mydb.list_collection_names():
            logger.info("Removing collection {coll_name}".format(**locals()))
            mycoll = mydb[MY_COLLECTION]       # create collection/Table In MongoDB, a collection is not created until it gets content!
            rCode = mycoll.drop()
            print("collection {coll_name} has been deleted RCode:{rCode}".format(**locals()))




# https://www.w3schools.com/python/python_mongodb_getstarted.asp
def mongow3school():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydatabase"]
    mycol = mydb["customers"]
    rCode = mycol.drop()
    mycol = mydb["customers"]

    mydict = { "name": "John", "address": "Highway 37" }
    x = mycol.insert_one(mydict)
    mydict = { "name": "Peter", "address": "Lowstreet 27" }
    x = mycol.insert_one(mydict)

    mylist = [
      { "name": "Amy", "address": "Apple st 652"},
      { "name": "Hannah", "address": "Mountain 21"},
      { "name": "Michael", "address": "Valley 345"},
      { "name": "Sandy", "address": "Ocean blvd 2"},
      { "name": "Betty", "address": "Green Grass 1"},
      { "name": "Richard", "address": "Sky st 331"},
      { "name": "Susan", "address": "One way 98"},
      { "name": "Vicky", "address": "Yellow Garden 2"},
      { "name": "Ben", "address": "Park Lane 38"},
      { "name": "William", "address": "Central st 954"},
      { "name": "Chuck", "address": "Main Road 989"},
      { "name": "Viola", "address": "Sideway 1633"}
    ]

    x = mycol.insert_many(mylist)

    mylist = [
      { "_id": 1, "name": "John", "address": "Highway 37"},
      { "_id": 2, "name": "Peter", "address": "Lowstreet 27"},
      { "_id": 3, "name": "Amy", "address": "Apple st 652"},
      { "_id": 4, "name": "Hannah", "address": "Mountain 21"},
      { "_id": 5, "name": "Michael", "address": "Valley 345"},
      { "_id": 6, "name": "Sandy", "address": "Ocean blvd 2"},
      { "_id": 7, "name": "Betty", "address": "Green Grass 1"},
      { "_id": 8, "name": "Richard", "address": "Sky st 331"},
      { "_id": 9, "name": "Susan", "address": "One way 98"},
      { "_id": 10, "name": "Vicky", "address": "Yellow Garden 2"},
      { "_id": 11, "name": "Ben", "address": "Park Lane 38"},
      { "_id": 12, "name": "William", "address": "Central st 954"},
      { "_id": 13, "name": "Chuck", "address": "Main Road 989"},
      { "_id": 14, "name": "Viola", "address": "Sideway 1633"}
    ]

    x = mycol.insert_many(mylist)

    x = mycol.find_one()
    print("FIND ONE:")
    print(x)

    print()
    print("FIND ALL:")
    for x in mycol.find():
        print(x)


    print()
    print("Return only the names and addresses, not the _ids:")
    for x in mycol.find({},{ "_id": 0, "name": 1, "address": 1 }):
      print(x)

    print()
    print('This example will exclude "address" from the result:')
    for x in mycol.find({},{ "address": 0 }):
      print(x)

    print()
    print('Find document(s) with the address "Park Lane 38":')
    myquery = { "address": "Park Lane 38" }
    mydoc = mycol.find(myquery)
    for x in mydoc:
      print(x)

    print()
    print('Find documents where the address starts with the letter "S" or higher:')
    myquery = { "address": { "$gt": "S" } }
    mydoc = mycol.find(myquery)
    for x in mydoc:
      print(x)

    print()
    print('Find documents where the address starts with the letter "S":')
    myquery = { "address": { "$regex": "^S" } }
    mydoc = mycol.find(myquery)
    for x in mydoc:
      print(x)





if __name__ == '__main__':
    mongow3school()