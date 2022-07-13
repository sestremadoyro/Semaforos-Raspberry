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

    #def create(self, data = {}):
    #    from random import randint
    #    #Step 2: Create sample data
    #    names = ['Kitchen','Animal','State', 'Tastey', 'Big','City','Fish', 'Pizza','Goat', 'Salty','Sandwich','Lazy', 'Fun']
    #    company_type = ['LLC','Inc','Company','Corporation']
    #    company_cuisine = ['Pizza', 'Bar Food', 'Fast Food', 'Italian', 'Mexican', 'American', 'Sushi Bar', 'Vegetarian']
    #    for x in range(1, 501):
    #        business = {
    #            'name' : names[randint(0, (len(names)-1))] + ' ' + names[randint(0, (len(names)-1))]  + ' ' + company_type[randint(0, (len(company_type)-1))],
    #            'rating' : randint(1, 5),
    #            'cuisine' : company_cuisine[randint(0, (len(company_cuisine)-1))] 
    #        }
    #        #Step 3: Insert business object directly into MongoDB via insert_one
    #        result=self.db.reviews.insert_one(business)
    #        #Step 4: Print to the console the ObjectID of the new document
    #        print('Created {0} of 500 as {1}'.format(x,result.inserted_id))
    #    #Step 5: Tell us that you are done
    #    print('finished creating 500 business reviews')
    #    return '100'

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
        

