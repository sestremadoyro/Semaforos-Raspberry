from models.db import Db

class TLight:
    schema: {
        'number': { type: 'int' },
        'pins': [{ type: 'int' }]
    }

    #[R, A, V]
    defaultList = [
        { 'number': 1, 'pins': [17, 27, 22] },
        { 'number': 2, 'pins': [10,  9, 11] },
        { 'number': 3, 'pins': [ 5,  6, 13] },
        { 'number': 4, 'pins': [21, 20, 16] },
        { 'number': 5, 'pins': [ 7,  8, 25] },
        { 'number': 6, 'pins': [24, 23, 18] }
    ]

    def __init__(self):
        db = Db()
        self.db = db.getClient()
                
    def getList(self):
        trafficLights = self.db.trafficLights.find({})
        return trafficLights

    def getLights(self):
        len = self.getList().count()
        if len == 0:
            for item in self.defaultList:
                self.db.trafficLights.insert(item)

        #result = []
        list = self.getList()
        #for tr in list:
        #    result.insert(tr['number'], TrafficLights(tr['pins'][0], tr['pins'][1], tr['pins'][2]))
        #print(result)
        return list
        

