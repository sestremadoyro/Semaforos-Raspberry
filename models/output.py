from models.db import Db
import datetime

class Output:
    schema: {
        'year': { type: 'int' },
        'month': { type: 'int' },
        'day': { type: 'int' },
        'plan': { type: 'int' },
        'moment': { type: 'int' },
        'duration': { type: 'int' },        
        'start': { type: 'string' },
        'end': { type: 'string' },
        'intervals': [{
            'number': { type: 'int' },
            'duration': { type: 'int' },
            'fases': [{
                'fase': { type: 'int' },
                'state': { type: 'string' },
                'red': { type: 'boolean' },
                'amber': { type: 'boolean' },
                'green': { type: 'boolean' },
                'green2': { type: 'boolean' }
            }]
        }],
        'created': { type: 'datetime' }
    }

    def __init__(self):
        db = Db()
        self.db = db.getClient()

    def create(self, data = {}):
        data['created'] = datetime.datetime.now()
        result = self.db.outputs.insert(data)
        return result

    def deleteAll(self):
        return self.db.outputs.delete_many({})
       

