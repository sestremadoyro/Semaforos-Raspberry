from models.db import Db
import datetime

class State:
    schema: {
        'action': { type: 'string' },
        'led': { type: 'string' },
        'duration': { type: 'int' },
        'startHour': { type: 'string' },
        'endHour': { type: 'string' },
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
        state = self.db.states.find_one({})
        self.db.states.update({"_id":state['_id']},{"$set":data})
        return state

    def execute(self, working):
        state = self.db.states.find_one({})  
        self.db.states.update({"_id":state['_id']},{"$set":{"executing":datetime.datetime.now(), "working": working}})
       
    def get(self):
        state = self.db.states.find_one({})
        return state

