import pymongo

class DBConnectorUtil :
    
    myclient = None
    mydb = None
    mycol = None
    
    def __init__(self, collection = None):
        print("Making a new Connection")
        self.myclient = pymongo.MongoClient("mongodb://10.3.101.179:1434/",connect=False) # Connection.
        self.mydb = self.myclient["meterDataArchival"] # DB Name.
        if(collection is not None) :
            self.mycol = self.mydb[collection]
    def getClient(self) :
        return self.myclient
    def closeClient(self) :
        print(f'{self} client is closed')
        self.myclient.close()
    def getDbObject(self) :
        return self.mydb
    def getCollectionObject(self) :
        return self.mycol