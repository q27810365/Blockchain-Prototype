import pymongo
# if fail to handshake to mongodb, release the content below
# import certifi
'''
About MongoDB
Database -> Collections -> Documents
Documents like records, we use Dictionary Type(JSON dict{key1: value1, key2: value2,...}) in Python
'''
# db.blockchain.createIndex({'hash':'text'},{unique:true})
# db.transactions.createIndex({'hash':'text'},{unique:true})
# db.ptransactions.createIndex({'hash':'text'},{unique:true})


class MongoDB:
    # Should change to your MongoDB setting

    # if fail to handshake to mongodb, release the content below
    # ca = certifi.where()
    __settings = {
        # "uri": "mongodb+srv://test1:a12345@comp5521.banljfk.mongodb.net/",
        "uri": "mongodb://localhost:27017",
        "db": "test",
    }

    def __init__(self):
        self.connect_client = pymongo.MongoClient(self.__settings["uri"])
        # if fail to handshake to mongodb, release the content below
        # self.connect_client = pymongo.MongoClient(self.__settings["uri"], tlsCAFile=self.ca)

        self.mydb = self.connect_client[self.__settings["db"]]
        # dblist = self.connect_client.list_database_names()
        # if len(dblist) != 0:
        #     print("connect sucessfully")
        #     print("DB is " + self.__settings["db"])

    # QUERY RECORDS
    # Get all documents in column col without mongodb auto-generated _id
    def getAll(self, collection):
        mycol = self.mydb[collection]
        return mycol.find({}, {"_id": 0})

    # Get documents from customized query in column col without mongodb auto-generated _id
    def get(self, collection, query, setting=None):  # default setting is none but results will not contain _id
        setting0 = {"_id": 0}
        if setting is not None:
            setting0.update(setting)
        mycol = self.mydb[collection]
        return mycol.find(query, setting0)

    # Get last block
    # db.collection.find().limit(1).sort([('$natural',-1)])
    def getlast(self, collection):
        return self.getAll(collection).limit(1).sort([('$natural', -1)])

    def getlast1(self, collection):
        return self.getAll(collection).sort('index', -1).limit(1)

    # Get last N block
    # db.collection.find().sort({ $natural: -1 }).limit(N)
    def getlastn(self, collection, n):
        return self.getAll(collection).limit(n).sort([('$natural', -1)])

    def getLongestChain(self) -> list:
        chain = []
        pointer = None
        for x in self.getlast('blockchain'):
            pointer = x
        if pointer is None:
            return []
        while pointer["prevHash"] != '':
            temp = {
                "hash": pointer["prevHash"]
            }
            for x in self.get('blockchain', temp):
                chain.append(x)
                pointer = x
        return chain

    # ADDITION documents
    # Add one document, value should be dict
    def insertOne(self, collection, value):
        mycol = self.mydb[collection]
        mycol_id = mycol.insert_one(value)
        return mycol_id.inserted_id  # return _id

    # Add documents, value_list should be dictlist eg: data[{dict1,dict2,...}]
    def insert(self, collection, value_list):
        mycol = self.mydb[collection]
        mycol_id = mycol.insert_many(value_list)
        return mycol_id.inserted_ids

    # UPDATE [not necessary?]
    # Update one document
    def update_one(self, collection, search_col, update_col):
        pass

    # Update documents
    def update(self, collection, search_col, update_col):
        pass

    # DELETE [not necessary?]
    # Delete one document
    def deleteOne(self, collection, query):
        my_col = self.mydb[collection]
        try:
            result = my_col.delete_one(query)
            return result
        except TypeError as e:
            print('Variables should be Dict')
            return None

    # Delete documents
    # Use Regular Expression,
    # eg: Delete all documents that start with F in the name field
    # query = { "name": {"$regex": "^F"} }
    def delete(self, collection, query):
        my_col = self.mydb[collection]
        try:
            result = my_col.delete_many(query)
            print(result.deleted_count, "pending transactions deleted")
            return result
        except TypeError as e:
            print('Variables should be Dict')
            return None

    # drop collection !!!It will delete the index
    def drop_collection(self, cols):
        my_col = self.mydb[cols]
        result = my_col.drop()
        return result

    # Get all connections
    def get_connections(self):
        return self.mydb.list_collection_names()

    # Close connection
    def close_connect(self):
        self.connect_client.close()
        return 'mongo\'s connection closed'
