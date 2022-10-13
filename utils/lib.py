import socket
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
    
    def verifyWeek(self):
        dfw = self.weekday()
        
        oweek = Week()
        ostate = State()
        oplan = Plan()

        plans = oweek.getList({'day': dfw})
        
        hour = datetime.now().strftime("%X")
        
        for pl in plans:
            if pl['active'] and hour >= (pl['start'] + ':00') and hour < (pl['end'] + ':00'):
                if pl['state'] == "ER":
                    ostate.save({'action': 'on', 'state': 'ER', 'active': True, 'duration': -1, 'led': 'R', 'startHour': pl['start'], 'endHour': pl['end']})
                if pl['state'] == "TR":
                    ostate.save({'action': 'blink', 'state': 'TR', 'active': True, 'duration': -1, 'led': '', 'startHour': pl['start'], 'endHour': pl['end']})
                if pl['state'] == "FN" and pl['plan'] is not None:
                    ostate.save({'action': 'plan', 'state': 'FN', 'active': True, 'duration': -1, 'led': '', 'startHour': pl['start'], 'endHour': pl['end']})
                    oplan.deleteAll()
                    oplan.create(pl['plan'])

                return