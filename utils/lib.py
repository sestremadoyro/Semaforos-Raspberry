import socket
import os
import sys
from models.plan import Plan
from models.state import State
from models.week import Week
from datetime import datetime

class Lib:

    def host(self):
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
    
        return {
            'hostname': hostname,
            'ip': IP
        }

    def weekday(self):
        # get current datetime
        dt = datetime.now()
        # get day of week as an integer
        return dt.isoweekday()

    def seconds(self, start, end):
        if (start == '' or start is None) or (end == '' or end is None): 
            return 30
        sec1 = (int(start[0:2]) * 60 * 60) + (int(start[-2:]) * 60) 
        sec2 = (int(end[0:2]) * 60 * 60) + (int(end[-2:]) * 60) 
        return sec2 - sec1

    def getEndHour(self, start, duracion):
        seconds = ((int(start[0:2]) * 60 * 60) + (int(start[-2:]) * 60)) + duracion

        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
     
        return "%02d:%02d" % (hour, minutes)
        
    def killTask(self):
        lines = self.execute("sudo pkill -f task.py")
        print(lines)
        
    
    def execute(self, command):
        from subprocess import PIPE, run

        result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        return result.stdout


    def taskRunning(self):               
        lines = self.execute("ps ax | grep task.py").splitlines()

        same = 0
        count1 = 0
        count2 = 0
        pid = os.getpid()
        
        if len(lines) > 1:
            for lin in lines:
                if '/bin/python' in lin:
                    if str(pid - 1) in lin or str(pid) in lin:
                        same = same + 1
                    else:
                        if '/bin/sh' in lin:
                            count1 = count1 + 1
                        else:
                            count2 = count2 + 1
                                
        if count2 > 1:
            os.system("sudo pkill -f task.py")
            count2 = 0

        return count2 > 0


    def verifyWeek(self):
        dfw = self.weekday()
        
        oweek = Week()
        ostate = State()
        oplan = Plan()

        plans = oweek.getList({'day': dfw})
        
        hour = datetime.now().strftime("%X")
        
        for pl in plans:
            if pl['active'] and hour >= (pl['start'] + ':00') and hour < (pl['end'] + ':00'):
                secs = self.seconds(pl['startHour'],pl['endHour'])
                if pl['state'] == "ER":
                    ostate.save({'action': 'on', 'state': 'ER', 'active': True, 'duration': secs, 'led': 'R', 'startHour': pl['start'], 'endHour': pl['end']})
                if pl['state'] == "TR":
                    ostate.save({'action': 'blink', 'state': 'TR', 'active': True, 'duration': secs, 'led': '', 'startHour': pl['start'], 'endHour': pl['end']})
                if pl['state'] == "FN" and pl['plan'] is not None:
                    ostate.save({'action': 'plan', 'state': 'FN', 'active': True, 'duration': secs, 'led': '', 'startHour': pl['start'], 'endHour': pl['end']})
                    plan = oplan.first({})
                    if plan is None:
                        oplan.create(pl['plan'])
                    else:
                        oplan.update(plan, pl['plan'])
                    

                return