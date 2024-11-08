from pymongo import MongoClient


uri = "mongodb+srv://mohfaiz0504:mohfaiz543@cluster0.nmg1vs4.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)
db = client["inventory"]
collection = db["order"]
print(collection.count_documents({}))