import sys
from models.task import Task
from utils.lib import Lib
import datetime

lib = Lib()

oTask = Task()
list = oTask.getList({'completed': False})


# GIT        => Actualizar App
# RESTART    => Reiniciar App
# DEL_LOG    => Eliminar LOG
# OTHER      => Otros
for task in list:
    
    if task['type'] == 'GIT':
        commands = [
            "cd /home/semaforo/api-raspberry",
            "sudo git stash",
            "sudo git pull",
            "sudo chown -R root:www-data /home/semaforo/api-raspberry",
            "sudo chmod -R 777 /home/semaforo/api-raspberry",
            "sudo chmod +x task.py",
            "sudo chmod +x work.py",
        ];

        for com in commands:
            lib.execute(com)

    if task['type'] == 'RESTART':
        lib.execute("sudo systemctl restart raspberry")

    if task['type'] == 'DEL_LOG':
        commands = [
            "cd /home/semaforo/api-raspberry",
            "sudo rm cron.log"
        ];

        for com in commands:
            lib.execute(com)

    if task['type'] == 'OTHER':
        lib.execute(task.commands)

    oTask.update(task, {'completed': True, 'completeDate': datetime.datetime.now()})

sys.exit()

