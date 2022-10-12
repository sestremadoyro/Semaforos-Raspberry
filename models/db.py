from pymongo import MongoClient
import pymongo
from time import sleep

# Provide the mongodb atlas url to connect python to mongodb using pymongo
# admin:123456@
CONNECTION_STRING = "mongodb://localhost:27017/raspberry"

class Db:

    def getClient(self):
        client = None
        count = 0
        while client is None and count < 10: 
            try:
                client = MongoClient(CONNECTION_STRING)
            except pymongo.errors.ConnectionFailure as e:
                client = None
                count = count + 1
                sleep(1)
                print(e)
        
        #print(client.list_database_names())
        
        #print(client['raspberry'].list_collection_names())
        #client['raspberry'].reviews.drop()

        # Create the database for our example (we will use the same database throughout the tutorial
        return client['raspberry']        
