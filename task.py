'''
	Raspberry Pi GPIO Status and Control
'''
import RPi.GPIO as GPIO
import sys
from time import sleep
from gpiozero import LED, TrafficLights
from models.plan import Plan
from models.trafficLight import TLight
from models.state import State
from models.output import Output
import datetime
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

tlight = TLight()
list = tlight.getLights()

lights = []
for tr in list:
    lights.insert(tr['number'], TrafficLights(tr['pins'][0], tr['pins'][1], tr['pins'][2]))

# turn leds OFF 
for x in lights:
  x.off();


oplan = Plan()
plan = oplan.first({'active': True})

ostate = State()
state = ostate.get()

ooutput = Output()

if plan is not None and state is not None and state['action'] == 'plan' and state['active']:
    ostate.execute(True)
    next = True
    outputs = []
    accumulated = 0
    
    #lights.insert(tr['number'], TrafficLights(tr['pins'][0], tr['pins'][1], tr['pins'][2]))
    while next == True:   
        created = datetime.datetime.now()
        output = { 
            'year': created.year,
            'month': created.month,
            'day': created.day,
            'plan': plan['code'],
            'moment': plan['moments'],
            'duration': 0,        
            'start': created.strftime("%X"),
            'end': '',
            'intervals': [],
        }
        for inter in plan['intervals']:
            fases = []
            for fase in plan['fases']:
                if inter['fase' + str(fase)] is not None:
                    led = inter['fase' + str(fase)]
                    actuator = lights[int(fase)-1]
                    actuator.off()
                    if led == 'R' or led == 'RA':
                        actuator.red.on()
                    if led == 'A' or led == 'RA' or led == 'VA':
                        actuator.amber.on()
                    if led == 'V' or led == 'VA':
                        actuator.green.on()
                #salida
                fases.insert(fase-1,{
                    'fase': fase,
                    'state': led,
                    'red': actuator.red.is_lit,
                    'amber': actuator.amber.is_lit,
                    'green': actuator.green.is_lit,
                    'green2': False
                });            
            ostate.save({'interval': inter['number'], 'duration': inter['duration'], 'accumulated': accumulated})            
            sleep(inter['duration'])
            accumulated += inter['duration']
            #salida
            output['duration'] += inter['duration']
            output['intervals'].insert(inter['number']-1,{
                'number': inter['number'],
                'duration': inter['duration'],
                'fases': fases
            })
        
        for inter in plan['intervals']:
            for fase in plan['fases']:
                if inter['fase' + str(fase)] is not None:
                    actuator = lights[int(fase)-1]
                    actuator.off()

        #plan
        plan['moments'] = plan['moments'] + 1
        oplan.update(plan, {'moments': plan['moments']})
        
        #salida
        finished = datetime.datetime.now()
        output['end'] = finished.strftime("%X")
        ooutput.create(output);

        if plan['moments'] < plan['cycles']:
            next = True
        else:
            next = False
                       
        state = ostate.get()
        if state is not None and state['action'] == 'plan' and state['active']:
            next = True
        else:
            next = False

ostate.save({'working': False})
sys.exit()

dct = {}
dct.__setitem__('a', 21)
print(dct)