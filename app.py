'''
	Raspberry Pi GPIO Status and Control
'''
import RPi.GPIO as GPIO
import socket
from flask import Flask, jsonify, render_template, request, url_for
from time import sleep
from gpiozero import LED, TrafficLights
from models.plan import Plan
from models.trafficLight import TLight
from models.state import State
from utils.sensor import Sensor
app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

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

    templateData = {
    	'state'  : state,
    	'plan'  : plan
    }
    #if state is not None:
    #    templateData['action'] = state['action']
    #    templateData['led'] = state['led']
    #    templateData['duration'] = state['duration']
    #    templateData['active'] = state['active']

    #if plan is not None:
    #    templateData['nroIntervals'] = plan['nroIntervals']
    #    templateData['nroFases'] = plan['nroFases']
    #    templateData['intervals'] = plan['intervals']
    #    templateData['fases'] = plan['fases']

    return render_template('index.html', **templateData)


@app.route("/manual/<action>")
def manual(action):
    ostate = State()
    oplan = Plan()
    state = ostate.get()
    if state is not None:
        if action == "red":
            ostate.save({'action': 'on', 'state': 'ER', 'active': True, 'duration': -1, 'led': 'R'})
        if action == "off":
            ostate.save({'action': 'off', 'state': 'OFF', 'active': False, 'duration': -1, 'led': ''})
        if action == "blink":
            ostate.save({'action': 'blink', 'state': 'TR', 'active': True, 'duration': -1, 'led': ''})
        if action == "plan":
            ostate.save({'action': 'plan', 'state': 'FN', 'active': True, 'duration': -1, 'led': ''})
        state_execute()
        state = ostate.get()
    plan = oplan.first({'active': True})
    templateData = {
    	'state'  : state,
    	'plan'  : plan
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
    #for x in list:
    #    print(x)

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
        cmd='nohup python -u task.py > task.log &'
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
                actuator.off()

            if model['active']:
                for fase in model['fases']:
                    led = model['led']
                    actuator = lights[int(fase)-1]
                    if led == '' and model['action'] == 'blink':
                        led == 'A'

                    if led == 'R':
                        actuator = actuator.red
                    if led == 'A':
                        actuator = actuator.amber
                    if led == 'V':
                        actuator = actuator.green
                    actuator.off()
                    if model['action'] == 'on':
                        actuator.on()
                    if model['action'] == 'off':
                        actuator.off()
                    if model['action'] == 'blink':
                        actuator.blink()

                if model['state'] == 'TR' and model['action'] == 'blink' and model['reds'] is not None:
                    for fase in model['reds']:
                        actuator = lights[int(fase)-1]
                        actuator.off()
                        actuator.red.blink()

                ostate.execute(False)
                exec = 'true'
                if model['duration'] > 0:
                    sleep(model['duration'])
                    for fase in model['fases']:
                        actuator = lights[int(fase)-1]
                        actuator.off()

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
    hostname = socket.gethostname()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    
    return jsonify({
        'hostname': hostname,
        'ip': IP
    })


state_execute();

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000, debug=True)
      