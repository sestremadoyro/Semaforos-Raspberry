from models.db import Db
import datetime

class State:
    schema: {
        'action': { type: 'string' },
        'led': { type: 'string' },
        'duration': { type: 'int' },
        'fases': [{ type: 'int' }],
        'active': [{ type: 'boolean' }],
        'executing': { type: 'datetime' },
        'interval': { type: 'int' },
        'duration': { type: 'int' },
    }

    def __init__(self):
        db = Db()
        self.db = db.getClient()

    def save(self, data):
        if self.db is None:
            return None
        state = self.db.states.find_one({})
        self.db.states.update({"_id":state['_id']},{"$set":data})
        return state

    def execute(self, working):
        if self.db is None:
            return None
        state = self.db.states.find_one({})  
        self.db.states.update({"_id":state['_id']},{"$set":{"executing":datetime.datetime.now(), "working": working}})
       
    def get(self):
        if self.db is None:
            return None
        state = self.db.states.find_one({})
        return state

