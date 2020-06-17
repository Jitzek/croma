from vision.watersource_recognition import getPosWaterSource, getColorTemp
import Constants
from TaskCodes import TaskCodes as tc, translateTaskToString as translateTaskToString

from enum import Enum, unique, auto
@unique
class Stage(Enum):
    NONE = auto()
    FIND_WATER_SOURCE = auto()
    GO_TO_WATER_SOURCE = auto()
    MEASURE_TEMPERATURE = auto()

class MeasureTempOfWaterSource:
    prev_stage = Stage.NONE
    current_stage = Stage.FIND_WATER_SOURCE
    current_result = False

    def __init__(self, rbc, socket=False, vision_display=False):
        self.rbc = rbc
        self.socket = socket
        self.vision_display = vision_display
        self.task_string = translateTaskToString(tc.MEASURE_TEMP_OF_WATER_SOURCE)
    
    def reset(self):
        self.prev_stage = Stage.NONE
        self.current_stage = Stage.FIND_WATER_SOURCE
        self.current_result = False

    def _stage_to_string(self, stage):
        return {
            Stage.FIND_WATER_SOURCE: 'Looking for Water Source',
            Stage.GO_TO_WATER_SOURCE: 'Going to Water Source',
            Stage.MEASURE_TEMPERATURE: 'Measuring Temperature of Water Source'
        }.get(stage, 'NaN');

    def _socket_send_current_stage(self):
        if self.socket:
            if self.prev_stage != self.current_stage:
                self.socket.send(Constants.JSON_PREFIX.format('{', self.task_string, self._stage_to_string(self.current_stage), '', '', '}'))
                self.prev_stage = self.current_stage

    def execute(self):
        self._socket_send_current_stage()
        self._draw_point_of_interest()

        if self.current_stage == Stage.FIND_WATER_SOURCE:
            pos = getPosWaterSource(self.rbc.Camera.getImage(), self.rbc.Camera.getWidth(), self.rbc.Camera.getHeight())
            x = False
            y = False
            if pos is not False:
                self.current_stage = Stage.GO_TO_WATER_SOURCE
            else: self._spin()
            return False
                

        if self.current_stage == Stage.GO_TO_WATER_SOURCE:
            pos = getPosWaterSource(self.rbc.Camera.getImage(), self.rbc.Camera.getWidth(), self.rbc.Camera.getHeight())
            x = False
            y = False
            if pos is not False:
                x, y = pos
            
            if not x or not y:
                return False

            if self._goToPos(x, y):
                self.current_stage = Stage.MEASURE_TEMPERATURE
            return False
        
        if self.current_stage == Stage.MEASURE_TEMPERATURE:
            result = getColorTemp(self.rbc.Camera.getImage(), self.rbc.Camera.getWidth(), self.rbc.Camera.getHeight())
                
            if self.socket:
                if not self.current_result or self.current_result != result:
                    self.socket.send(Constants.JSON_PREFIX.format('{', self.task_string, 'Measuring Temperature', 'Temperature', result, '}'))
            self.current_result = result
            return False

    def _draw_point_of_interest(self):
        if self.vision_display:
            self.vision_display.setColor(0x09ff00)
            self.vision_display.drawRectangle(int(self.rbc.Camera.getWidth()/2), int(self.rbc.Camera.getHeight()/2), 20, 20)
    
    def _goToPos(self, x, y):
        x_dev = 1
        min_x = self.rbc.Camera.getWidth()/2 - x_dev
        max_x = self.rbc.Camera.getWidth()/2 + x_dev

        y_dev = 1
        min_y = self.rbc.Camera.getHeight()/2 - y_dev
        max_y = self.rbc.Camera.getHeight()/2 + y_dev

        if min_x < x < max_x:
            if min_y < y < max_y:
                return True
        if x < min_x:
            self.rbc.turnOnSpot(-3)
            return False
        if x > max_x:
            self.rbc.turnOnSpot(3)
            return False
        if y < min_y:
            self.rbc.goStraight(3)
            return False
        if y > max_y:
            self.rbc.turnOnSpot(-3)
            return False
        return False
    
    def _spin(self):
        self.rbc.turnOnSpot(3)