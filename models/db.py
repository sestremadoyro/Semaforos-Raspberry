from pymongo import MongoClient
import pymongo

# Provide the mongodb atlas url to connect python to mongodb using pymongo
# admin:123456@
CONNECTION_STRING = "mongodb://localhost:27017/raspberry"

class Db:

    def getClient(self):
        client = MongoClient(CONNECTION_STRING)
        #print(client.list_database_names())
        
        #print(client['raspberry'].list_collection_names())
        #client['raspberry'].reviews.drop()

        # Create the database for our example (we will use the same database throughout the tutorial
        return client['raspberry']
