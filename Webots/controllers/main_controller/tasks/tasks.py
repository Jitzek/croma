from tasks.dancing_on_the_moon import DancingOnTheMoon
from tasks.moon_maze import MoonMaze
from tasks.moon_survival import MoonSurvival
from tasks.measure_watersource_temp import MeasureTempOfWaterSource
from tasks.scan_qr import ScanQR
from tasks.find_card_symbol import FindCardSymbol
from tasks.mineral_analysis import MineralAnalysis

from TaskCodes import TaskCodes as tc
import TaskCodes

class Tasks:
    force_stop = False

    def __init__(self, rbc, socket = False, vision_display = False):
        self.rbc = rbc
        self.TASKS = {
            tc.DANCING_ON_THE_MOON: DancingOnTheMoon(self.rbc, socket, vision_display),
            tc.MOON_MAZE: MoonMaze(self.rbc, socket, vision_display),
            tc.MOON_SURVIVIVAL: MoonSurvival(self.rbc, socket, vision_display),
            tc.MEASURE_TEMP_OF_WATER_SOURCE: MeasureTempOfWaterSource(self.rbc, socket, vision_display),
            tc.SCAN_QR_CODE: ScanQR(self.rbc, socket, vision_display),
            tc.FIND_CARD_SYMBOL: FindCardSymbol(self.rbc, socket, vision_display),
            tc.MINERAL_ANALYSIS: MineralAnalysis(self.rbc, socket, vision_display)
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
    
