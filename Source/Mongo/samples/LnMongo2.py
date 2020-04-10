#!/usr/bin/python3
# updated by ...: Loreto Notarantonio
# Version ......: 30-03-2020 16.36.48
import sys
import pymongo
# from pymongo import MongoClient
import time
import json, yaml

import pymongo

class mongoDB():  # you don't need ()'s here - only if you are inheriting classes
                  # you could inherit from object here, which is a good practice
                  # by doing class mongoDb(object):, otherwise you can just take
                  # them out

    conn = object # here, you're defining a class member - global for all instances
                  # generally, you don't instantiate an object pointer like this,
                  # you would set it to None instead.  It won't fail doing this,
                  # but it's not "right"

    def __init__(self):
        # the __init__ method is the constructor method - this will
        # allow you to initialize a particular instance of your class, represented
        # by the self argument.  This method is called when you call the class, i.e.
        # inst = mongoDb()

        # in this case, the conn variable is not a global.  Globals are defined
        # at the root module level - so in this example, only pymongo is a global
        # conn is a class member, and would be accessed by doing mongoDB.conn
        global conn

        # with that being said, you're initializing a local variable here called conn
        # that is not being stored anywhere - when this method finishes, this variable
        # will be cleaned up from memory, what you are thinking you're doing here
        # should be written as mongoDB.conn = pymongo.Connection("localhost", 27017)
        conn = pymongo.Connection("localhost",27017)

    def CreateCollection(name =""):
        # there is one of two things you are trying to do here - 1, access a class
        # level member called conn, or 2, access an instance member called conn

        # depending on what you are going for, there are a couple of different ways
        # to address it.

        # all methods for a class, by default, are instance methods - and all of them
        # need to take self as the first argument.  An instance method of a class
        # will always be called with the instance first.  Your error is caused because
        # you should declare the method as:

        # def CreateCollection(self, name = ""):

        # The alternative, is to define this method as a static method of the class -
        # which does not take an instance but applies to all instances of the class
        # to do that, you would add a @staticmethod decorator before the method.

        # either way, you're attempting to access the global variable "conn" here,
        # which again does not exist

        # the second problem with this, is that you are trying to take your variable
        # argument (name) and use it as a property.  What python is doing here, is
        # looking for a member variable called name from the conn object.  What you
        # are really trying to do is create a collection on the connection with the
        # inputed name

        # the pymongo class provides access to your collections via this method as a
        # convenience around the method, create_collection.  In the case where you
        # are using a variable to create the collection, you would call this by doing

        # conn.create_collection(name)

        # but again, that assumes conn is what you think it is, which it isn't
        dbCollection  = conn.name
        return dbCollection

if __name__ == '__main__':
    # here you are just creating a pointer to your class, not instantiating it
    # you are looking for:

    # database = mongoDB()
    database = mongoDB

    # this is your error, because of the afore mentioned lack of 'self' argument
    collection = database.CreateCollection("Hello")