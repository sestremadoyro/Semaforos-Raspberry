from models.db import Db
import datetime

class Plan:
    schema: {
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
    }

    def __init__(self):
        db = Db()
        self.db = db.getClient()

    def create(self, data = {}):
        data['created'] = datetime.datetime.now()
        result = self.db.plans.insert_one(data)
        return result

    def update(self, plan, data):
        self.db.plans.update({"_id":plan['_id']},{"$set":data})
        return plan

    def deleteAll(self):
        return self.db.plans.delete_many({})

    def getList(self, filter = {}):
        plans = self.db.plans.find(filter)
        return plans

    def first(self, filter = {}):
        plan = self.db.plans.find_one(filter)
        return plan
        

