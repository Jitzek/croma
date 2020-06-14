from tasks.dancing_on_the_moon import DancingOnTheMoon
from tasks.moon_maze import MoonMaze
from tasks.moon_survival import MoonSurvival
from tasks.recognize_symbol import RecognizeSymbol
from tasks.recognize_temperature import RecognizeTemperature
from tasks.scan_qr import ScanQR

from TaskCodes import TaskCodes as tc
import TaskCodes

class Tasks:
    force_stop = False

    def __init__(self, rbc):
        self.rbc = rbc
        self.TASKS = {
            tc.DANCING_ON_THE_MOON: DancingOnTheMoon(self.rbc),
            tc.MOON_MAZE: MoonMaze(self.rbc),
            tc.MOON_SURVIVIVAL: MoonSurvival(self.rbc),
            tc.RECOGNIZE_SYMBOL: RecognizeSymbol(self.rbc),
            tc.RECOGNIZE_TEMPERATURE: RecognizeTemperature(self.rbc),
            tc.SCAN_QR_CODE: ScanQR(self.rbc)
        }
    
    def forceStop(self):
        self.force_stop = True
    
    def execTask(self, task_code):
        if self.force_stop:
            self.force_stop = False
            return False
        return self.TASKS.get(task_code, self._Default).execute()
    
    def resetAllActions(self):
        for key in self.TASKS:
            self.TASKS[key].reset()

    def _Default(self):
        return True
    
