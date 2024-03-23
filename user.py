from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['BoozeBuddy']

class User:
    def __init__(self, user_id):
        self.user_id = user_id

    @classmethod
    def get(cls, user_id):
        user_data = db.users.find_one({'_id': user_id})
        if user_data:
            return cls(user_data['_id'])
        return None