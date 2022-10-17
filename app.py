'''
	Raspberry Pi GPIO Status and Control
'''
import RPi.GPIO as GPIO
from flask import Flask, jsonify, render_template, request, url_for
from time import sleep
from gpiozero import LED, TrafficLights
from models.plan import Plan
from models.trafficLight import TLight
from models.state import State
from utils.sensor import Sensor
from utils.lib import Lib
import datetime
app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

lib = Lib()
tlight = TLight()
list = tlight.getLights()

lights = []
for tr in list:
    lights.insert(tr['number'], TrafficLights(tr['pins'][0], tr['pins'][1], tr['pins'][2]))


ledRedSts = 0
ledYlwSts = 0
ledGrnSts = 0
# Define button and PIR sensor pins as an input

# turn leds OFF 
for x in lights:
  x.off();

ostate = State()
ostate.execute(False)

print('Aplicacion Iniciada')
  
@app.route("/", methods=('GET', 'POST'))
def index():
    ostate = State()
    oplan = Plan()
    state = ostate.get()
    plan = oplan.first({'active': True})

    if request.method == 'POST':
        #result.insert(tr['number'], TrafficLights(tr['pins'][0], tr['pins'][1], tr['pins'][2]))
        intervals = [];
        for inter in plan['intervals']:
            if (request.form['duration_' + str(inter['number'])] is not None):
                inter['duration'] = request.form['duration_' + str(inter['number'])]
            for fase in plan['fases']:
                if inter['fase' + str(fase)] is not None and request.form['fase_' + str(inter['number']) + '_' + str(fase)] is not None:
                    inter['fase' + str(fase)] = request.form['fase_' + str(inter['number']) + '_' + str(fase)]
            intervals.insert(inter['number']-1, inter)
        plan['intervals'] = intervals
        oplan.update(plan, {'intervals': plan['intervals']})

    leds = []
    for fase in state['fases']:
        index = int(fase)-1
        actuator = lights[index]
        leds.insert(index,{
            'green': actuator.green.is_lit,
            'amber': actuator.amber.is_lit,
            'red': actuator.red.is_lit
        })
            
    templateData = {
    	'state'  : state,
    	'plan'  : plan,
    	'leds'  : leds,
        'host'  : lib.host()
    }

    return render_template('index.html', **templateData)


@app.route("/manual", methods=('GET', 'POST'))
def manual():
    ostate = State()
    oplan = Plan()
    state = ostate.get()
    plan = oplan.first()
    forceWork = False
    

    if request.method == 'POST':
        action = request.form['action']
        if state is not None:
            duration = 3600
            if request.form['duration'] is not None:
                duration = int(request.form['duration']) * 60

            startHour = lib.getEndHour(datetime.datetime.now().strftime("%X")[0:5],-5)
            endHour = lib.getEndHour(startHour,duration)

            if action == "red":
                ostate.save({'action': 'on', 'state': 'ER', 'active': True, 'duration': duration, 'led': 'R', 'startHour': startHour, 'endHour': endHour})
                forceWork = True
            if action == "blink":
                ostate.save({'action': 'blink', 'state': 'TR', 'active': True, 'duration': duration, 'led': 'A', 'startHour': startHour, 'endHour': endHour})
                forceWork = True
            if action == "off":
                ostate.save({'action': 'off', 'state': 'OFF', 'active': False, 'duration': -1, 'led': '', 'startHour': '00:00', 'endHour': '23:59'})
            if action == "plan":
                secs = lib.seconds(plan['startHour'],plan['endHour'])
                ostate.save({'action': 'plan', 'state': 'FN', 'active': True, 'duration': secs, 'led': '', 'startHour': plan['startHour'], 'endHour': plan['endHour']})
            state_execute()

    state = ostate.get()

    if forceWork == True:
        state['working'] = True

    leds = []
    for fase in state['fases']:
        index = int(fase)-1
        actuator = lights[index]
        leds.insert(index,{
            'green': actuator.green.is_lit,
            'amber': actuator.amber.is_lit,
            'red': actuator.red.is_lit
        })

    plan = oplan.first({'active': True})
    templateData = {
    	'state'  : state,
    	'plan'  : plan,
    	'leds'  : leds,
        'host'  : lib.host()
	}
    return render_template('index.html', **templateData)



@app.route("/light/<action>/<index>", methods=['POST'])
def event(action, index):   
    result = "false"
    if int(index) >= 0:
        actuator = lights[int(index)-1]
        if action == "blink":
            actuator.red.blink()
            actuator.amber.blink()
        if action == "on":
            actuator.on()
        if action == "off":
            actuator.off()        
        if actuator.is_lit:
            result = "true"

    response = app.response_class(
        response=result,
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/light/<led>/<action>/<index>", methods=['POST'])
def event_led(led, action, index):   
    result = "false"
    if int(index) >= 0:
        actuator = lights[int(index)-1]
        if led == 'red':
            actuator = actuator.red
        if led == 'yellow':
            actuator = actuator.amber
        if led == 'green':
            actuator = actuator.green
        if action == "blink":
            actuator.blink()
        if action == "on":
            actuator.on()
        if action == "off":
            actuator.off()        
        if actuator.is_lit:
            result = "true"

    response = app.response_class(
        response=result,
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/light/status/<index>", methods=['GET'])
def status(index):    
    result = "false"
    if int(index) >= 0:
        actuator = lights[int(index)-1]
        if actuator.is_lit:
            result = "true"

    response = app.response_class(
        response=result,
        status=200,
        mimetype='application/json'
    )
    return response



@app.route("/plans", methods=['POST'])
def plan_save():    
    plan = Plan()
    result = plan.create()

    response = app.response_class(
        response=result,
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/plans", methods=['GET'])
def plan_list():    
    plan = Plan()
    
    list = plan.getList({'active': True})

    response = app.response_class(
        response='true',
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/plans", methods=['DELETE'])
def plan_delete():    
    plan = Plan()
    result = plan.deleteAll()

    response = app.response_class(
        response=result,
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/plan-execute", methods=['POST'])
def plan_execute():
    ostate = State()
    model = ostate.get()

    if model['working'] == False:
        import subprocess
        #import sys
        cmd='nohup python -u /home/semaforo/api-raspberry/task.py > /home/semaforo/api-raspberry/manual.log &'
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #o, e = proc.communicate()
        #print('Error: '  + e.decode('ascii'))

        #import subprocess, signal
        #subprocess.Popen(['python3', 'my_script.py'],
        #   stdin = subprocess.DEVNULL,
        #   stdout = open('nohup.out', 'w'),
        #   stderr = subprocess.STDOUT,
        #   start_new_session = True,
        #   preexec_fn = (lambda: signal.signal(signal.NOHUP, signal.SIG_IGN)))

    response = app.response_class(
        response='true',
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/state", methods=['POST'])
def state_save(model):    
    state = State()
    result = state.save(model)

    response = app.response_class(
        response='true',
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/state", methods=['GET'])
def get_state():    
    state = State()
    model = state.get()
    sen = Sensor()

    oplan = Plan()
    plan = oplan.first({'active': True})

    if model is not None: 
        fases = []
        for fase in model['fases']:
            index = int(fase)-1
            actuator = lights[index]
            fases.insert(index,{
                'fase': fase,
                'green':actuator.green.is_lit,
                'amber': actuator.amber.is_lit,
                'red': actuator.red.is_lit
            })

        moments = 0
        executing = ''
        if plan is not None: 
            moments = plan['moments']
            
        if model['executing'] is not None: 
            executing = model['executing'].isoformat()

        return jsonify({
            'action': model['action'],
            'led': model['led'],
            'active': model['active'],
            'duration': model['duration'],
            'interval': model['interval'],
            'working': model['working'],
            'accumulated': model['accumulated'],
            'moments': moments,
            'executing': executing,
            'fases': fases,
            'sensor': sen.readLight()
        })
    else:
        return app.response_class(
            response='false',
            status=200,
            mimetype='application/json'
        )

@app.route("/state-execute", methods=['POST'])
def state_execute():    
    ostate = State()
    model = ostate.get()
    exec = 'false'

    if model is not None:
        if model['action'] == 'plan':
            plan_execute()
        else:
            for fase in model['fases']:
                actuator = lights[int(fase)-1]
                actuator.red.off()
                actuator.amber.off()
                actuator.green.off()
                actuator.off()

            ostate.execute(False)

            import os
            cmd = 'pkill -f task.py'
            os.system(cmd)

            if model['active'] and model['action'] != 'off':
                for fase in model['fases']:
                    led = model['led']
                    actuator = lights[int(fase)-1]
                    if led == '' and model['action'] == 'blink':
                        led = 'A'

                    if led == 'R':
                        actuator = actuator.red
                    if led == 'A':
                        actuator = actuator.amber
                    if led == 'V':
                        actuator = actuator.green
                    actuator.off()
                    if model['action'] == 'on':
                        actuator.on()
                    if model['action'] == 'blink':
                        actuator.blink()

                if model['state'] == 'TR' and model['action'] == 'blink' and model['reds'] is not None:
                    for fase in model['reds']:
                        actuator = lights[int(fase)-1]
                        actuator.amber.off()
                        actuator.red.blink()

                ostate.execute(True)

            exec = 'true'
            

    #if model['action'] != 'off':
    #    sleep(1)

    response = app.response_class(
        response = exec,
        status=200,
        mimetype='application/json'
    )
    return response

@app.route("/calibrate", methods=['GET'])
def calibrate():    
    sen = Sensor()
    actuator = lights[0]

    off_min = 100
    off_max = 0
    actuator.off();
    i = 1
    while i <= 10:
        value = sen.read()
        if value < off_min:
            off_min = value
        if value > off_max:
            off_max = value
        sleep(200/1000)
        i += 1

    on_min = 100
    on_max = 0
    actuator.green.on();
    i = 1
    while i <= 10:
        value = sen.read()
        if value < on_min:
            on_min = value
        if value > on_max:
            on_max = value
        sleep(200/1000)
        i += 1
    
    actuator.off();

    return jsonify([{
        'mode': 'OFF',
        'min': off_min,
        'max': off_max
    },{
        'mode': 'ON',
        'min': on_min,
        'max': on_max,
    }])



@app.route("/host", methods=['GET'])
def get_host():    
    return jsonify(lib.host())



if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000, debug=True)
      