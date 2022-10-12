from models.db import Db

class TLight:
    schema: {
        'number': { type: 'int' },
        'pins': [{ type: 'int' }]
    }

    #[R, A, V]
    defaultList = [
        { 'number': 1, 'pins': [22, 27, 17] },
        { 'number': 2, 'pins': [11,  9, 10] },
        { 'number': 3, 'pins': [13,  6,  5] },
        { 'number': 4, 'pins': [16, 20, 21] },
        { 'number': 5, 'pins': [25,  8,  7] },
        { 'number': 6, 'pins': [18, 23, 24] }
    ]

    def __init__(self):
        db = Db()
        self.db = db.getClient()
                
    def getList(self):
        if self.db != None:
            trafficLights = self.db.trafficLights.find({})
            return trafficLights
        else:
            return []

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
        

