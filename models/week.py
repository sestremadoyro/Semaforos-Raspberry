from models.db import Db
import datetime

class Week:
    schema: {
        'code': { type: 'int' },
        'day': { type: 'int' },
        'number': { type: 'int' },   
        'state': { type: 'string' },
        'active': { type: 'boolean' },
        'start': { type: 'string' },
        'end': { type: 'string' },        
        'plan': {
            'code': { type: 'int' },
            'name': { type: 'string' },
            'waitTime': { type: 'int' },
            'cycleTime': { type: 'int' },
            'startHour': { type: 'string' },
            'endHour': { type: 'string' },
            'nroIntervals': { type: 'int' },
            'nroFases': { type: 'int' },
            'syncRT': { type: 'boolean' },
            'active': { type: 'boolean' },
            'moments': { type: 'int' },
            'cycles': { type: 'int' },
            'fases': [{ type: 'int' }],
            'intervals': [{ type: 'int' }],
            'updated': { type: 'datetime' },
            'created': { type: 'datetime' }
        },
        'created': { type: 'datetime' }
    }

    def __init__(self):
        db = Db()
        self.db = db.getClient()

    def getList(self, filter = {}):
        weeks = self.db.weeks.find(filter)
        return weeks

       


