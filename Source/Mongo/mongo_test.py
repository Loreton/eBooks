#!/usr/bin/python3
#
# updated by ...: Loreto Notarantonio
# Version ......: 27-03-2020 16.49.51
#
import sys; sys.dont_write_bytecode = True
import pymongo
import json, yaml

# https://www.w3schools.com/python/python_mongodb_create_collection.asp
# https://realpython.com/introduction-to-mongodb-and-python/
# http://docs.mongoengine.org/tutorial.html

def db_exists(mydb):
    dblist = mydb.list_database_names()
    if "mydatabase" in dblist:
      print("The database exists.")

def dict_to_yaml(my_dict, sort_keys=True):
    assert isinstance(my_dict, dict)
    # print(isinstance(my_dict, dict))
    # xx_json = json.dumps(my_dict, indent=4, sort_keys=True)
    my_json = json.dumps(my_dict, sort_keys=sort_keys)
    my_yaml = yaml.dump(yaml.load(my_json), default_flow_style=False)
    return my_yaml


from pymongo import MongoClient
import time

# epoch time before API call
start = time.time()

try:

    # attempt to create a client instance of PyMongo driver
    client = MongoClient(host = ["localhost:1111"], serverSelectionTimeoutMS = 2000)

    # call the server_info() to verify that client instance is valid
    client.server_info() # will throw an exception

except:
    print ("connection error")
    # print the time that has elapsed
    print (time.time() - start)


sys.exit()

client = pymongo.MongoClient("mongodb://localhost:27017/")
print (client)

"""
            create DB
Remember: In MongoDB, a database is not created until it gets content,
so if this is your first time creating a database, you should complete
the next two chapters (create collection and create document)
before you check if the database exists
"""
client = pymongo.MongoClient("mongodb://localhost:27017/")
# client = pymongo.MongoClient()
# client = pymongo.MongoClient('localhost', 27017) # connection
mydb = client["db_test"]        # create DB In MongoDB, a database is not created until it gets content
# MY_COLLECTION = 'customers'

MY_COLLECTION = 'posts'
if MY_COLLECTION in mydb.list_collection_names():
    print("The collection {MY_COLLECTION} exists.".format(**locals()))
    mycol = mydb[MY_COLLECTION]       # create collection/Table In MongoDB, a collection is not created until it gets content!
    rCode = mycol.drop()
    print("The collection {MY_COLLECTION} deleted {rCode}".format(**locals()))

mycol = mydb[MY_COLLECTION]       # create collection/Table In MongoDB, a collection is not created until it gets content!
if MY_COLLECTION in mydb.list_collection_names():
    print ('created collection: {MY_COLLECTION}').format(**locals())

# posts = mydb[MY_COLLECTION]       # create collection/Table In MongoDB, a collection is not created until it gets content!
post_data = {
    'title': 'Python and MongoDB',
    'content': 'PyMongo is fun, you guys',
    'author': 'Scott'
}
result = mycol.insert_one(post_data)
print('One post: {0}'.format(result.inserted_id))

"""
    We can even insert many documents at a time, which is much faster
    than using insert_one() if you have many documents to add to the database.
    The method to use here is insert_many().
    This method takes an array of document data:
"""
post_1 = {
    'title': 'Python and MongoDB',
    'content': 'PyMongo is fun, you guys',
    'author': 'Scott'
}
post_2 = {
    'title': 'Virtual Environments',
    'content': 'Use virtual environments, you guys',
    'author': 'Scott'
}
post_3 = {
    'title': 'Learning Python',
    'content': 'Learn Python, it is easy',
    'author': 'Bill'
}
new_result = mycol.insert_many([post_1, post_2, post_3])
print('Multiple posts: {0}'.format(new_result.inserted_ids))

"""
    To retrieve a document, we’ll use the find_one() method.
    The lone argument that we’ll use here (although it supports many more)
    is a dictionary that contains fields to match. In our example below,
    we want to retrieve the post that was written by Bill:
"""

post = mycol.find_one({'author': 'Bill'})
print('\n   retrieving single:')
print('     ', post)


posts = mycol.find({'author': 'Scott'})
for post in posts:
    print('\n   retrieving multiple:')
    print('     ', post)
