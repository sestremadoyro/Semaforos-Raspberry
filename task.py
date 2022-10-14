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
from models.week import Week
from utils.sensor import Sensor
from utils.lib import Lib
import datetime
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

lib = Lib()
lib.verifyWeek()

tlight = TLight()
list = tlight.getLights()

ostate = State()
state = ostate.get()

hour = datetime.datetime.now().strftime("%X")

if state is not None and state['working'] == False and hour >= (state['startHour'] + ':00') and hour < (state['endHour'] + ':00'):

    lights = []
    for tr in list:
        lights.insert(tr['number'], TrafficLights(tr['pins'][0], tr['pins'][1], tr['pins'][2]))

    # turn leds OFF 
    for x in lights:
        x.off();
    
    if ((state['action'] == 'on' and state['state'] == 'ER') or (state['action'] == 'blink' and state['state'] == 'TR')) and state['active'] and state['duration'] > 0:
        ostate.execute(True)
        next = True

        for fase in state['fases']:
            led = state['led']
            actuator = lights[int(fase)-1]
            if led == '' and state['action'] == 'blink':
                led = 'A'

            if led == 'R':
                actuator = actuator.red
            if led == 'A':
                actuator = actuator.amber
            if led == 'V':
                actuator = actuator.green
            actuator.off()
            if state['action'] == 'on':
                actuator.on()
            if state['action'] == 'blink':
                actuator.blink()

        if state['action'] == 'blink' and state['reds'] is not None:
            for fase in state['reds']:
                actuator = lights[int(fase)-1]
                actuator.amber.off()
                actuator.red.blink()
        
        secs = lib.seconds(state['startHour'],state['endHour'])
        acum = 0        
        add = 10

        while next == True:   
            sleep(add)
            add = 10
            if secs - acum < 10:
                add = secs - acum
            acum = acum + add

            state = ostate.get()
            if state is not None and (state['action'] == 'on' and state['state'] == 'ER') or (state['action'] == 'blink' and state['state'] == 'TR') and state['active'] and next == True:
                next = True
            else:
                next = False

            hour = datetime.datetime.now().strftime("%X")
            if state is not None and hour >= (state['startHour'] + ':00') and hour <= (state['endHour'] + ':00') and next == True:
                next = True
            else:
                next = False

            if acum < secs and next == True:
                next = True
            else:
                next = False

    
    oplan = Plan()
    plan = oplan.first({'active': True})
    
    if plan is not None and state['action'] == 'plan' and state['active']:
        sen = Sensor()    
        ooutput = Output()

        ostate.execute(True)
        next = True
        outputs = []
        accumulated = 0
        
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
                    'sensor': sen.readLight(),
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
                        
            state = ostate.get()
            plan = oplan.first({'active': True})

            if plan is not None and plan['moments'] < plan['cycles']:
                next = True
            else:
                next = False
                       
            if state is not None and state['action'] == 'plan' and state['active'] and next == True:
                next = True
            else:
                next = False

            hour = datetime.datetime.now().strftime("%X")
            if hour >= (state['startHour'] + ':00') and hour <= (state['endHour'] + ':00') and next == True:
                next = True
            else:
                next = False
    
    ostate.execute(False)

    print('task finised => ' + hour)
    
    dct = {}
    dct.__setitem__('a', 21)
    print(dct)

    sys.exit()