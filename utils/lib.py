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
        plans = oweek.getList({'day': dfw})
        
        hour = datetime.datetime.now().strftime("%X")
        console.log(plans);
        console.log(hour);
        
        for pl in plans:
            if pl['active'] and hour >= (pl['start'] + ':00') and hour < (pl['end'] + ':00'):
                console.log(pl);
                return