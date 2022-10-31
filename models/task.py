from models.db import Db
import datetime

class Task:
    schema: {
        'code': { type: 'int' },
        'name': { type: 'string' },
        'type': { type: 'string' },
        'commands': [{ type: 'string' }],
        'completed': { type: 'boolean' },
        'taskDate': { type: 'datetime' },
        'completeDate': { type: 'datetime' }
    }

    def __init__(self):
        db = Db()
        self.db = db.getClient()

    def update(self, task, data):
        self.db.tasks.update({"_id":task['_id']},{"$set":data})
        return task

    def deleteAll(self):
        return self.db['tasks'].delete({}) 

    def getList(self, filter = {}):
        tasks = self.db.tasks.find(filter)
        return tasks

        
