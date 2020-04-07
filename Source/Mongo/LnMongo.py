#!/usr/bin/python3
# updated by ...: Loreto Notarantonio
# Version ......: 07-04-2020 08.57.45
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
        self._record_fields = fields

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
        for _key in self._record_fields:
            if _key not in _keys:
                logger.info("{_key} is missing. Assigning ''".format(**locals()))
                record[_key] = ''

        """
            add '_id' field
            get the self._id_fields contents and join its words
        """

        # - check for extra fields
        for _key in record.keys():
            if not _key in self._record_fields:
                print("field {_key} is not included in the record_fields".format(**locals()))
                logger.error('record', record)
                logger.error('fields', self._record_fields)
                _json = json.dumps(record, indent=4, sort_keys=True)
                print("Record:\n    ", _json)
                _json = json.dumps(self._record_fields, indent=4, sort_keys=True)
                print("Record Fields:\n    ", _json)
                sys.exit(1)

        _id = []
        for fld in self._id_fields:
            _id.extend(record[fld].split())
        record['_id'] = '_'.join(_id)

        return record


    def insert(self, post_data, replace=False):
        assert isinstance(post_data, (list, dict))
        records = [post_data] if isinstance(post_data, dict) else post_data

        ret_value = {}
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
                result = self._collection.insert_one(my_rec)
                status  = result.inserted_id

            ret_value[index] = status

        return ret_value


    def update(self, post_data):
        assert isinstance(post_data, (list, dict))
        inp_data = [post_data] if isinstance(post_data, dict) else post_data

        # result = db.test.update_one({'x': 1}, {'$inc': {'x': 3}})
        my_data = self.checkFields(inp_data)
        result = self._collection.insert_many(my_data)

        return result

    # https://docs.mongodb.com/manual/reference/operator/query/regex/
    def searchWord(self, search_text):
        # db.articles.find( { $text: { $search: "coffee" } } )
        return self._collection.find({"$text": {"$search": search_text}})


       # https://docs.mongodb.com/manual/reference/operator/query/regex/
    def search(self, field_name, regex, ignore_case=False):
        '''
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
        logger.console('my_query', query)
        result = self._collection.find(query).limit(10)
        logger.console('    record found', result.count())
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