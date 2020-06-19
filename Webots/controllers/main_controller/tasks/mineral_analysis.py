from enum import Enum, unique, auto
from vision.mineral_recognition import MineralRecognition
from vision.deposit_tray_recognition import distance_from_deposit_tray
from actions.collect_mineral import CollectMineral
from actions.weigh_object import WeighObject
from actions.deposit_object_into_tray import DepositObjectIntoTray
import Constants

@unique
class Stage(Enum):
    NONE = auto()
    SEARCH_FOR_MINERAL = auto()
    COLLECT_MINERAL = auto()
    WEIGH_MINERAL = auto()
    SEARCH_FOR_DEPOSIT_TRAY = auto()
    DEPOSIT_MINERAL_INTO_TRAY = auto()

class MineralAnalysis:
    WEIGHING_TIMEOUT = 64
    weighing_count = 0
    weights = []

    prev_stage = Stage.NONE
    current_stage = Stage.SEARCH_FOR_MINERAL

    def __init__(self, rbc, socket=False, vision_display=False):
        self.rbc = rbc
        self.socket = socket
        self.mr = MineralRecognition(self.rbc.Camera)
        self.cm = CollectMineral(self.rbc)
        self.wo = WeighObject(self.rbc)
        self.doit = DepositObjectIntoTray(self.rbc)
    
    def reset(self):
        self.current_stage = Stage.SEARCH_FOR_MINERAL
        self.mr = MineralRecognition(self.rbc.Camera)
        self.cm.reset()
        self.wo.reset()
        self.doit.reset()
        self.weighing_count = self.WEIGHING_TIMEOUT


    def _stage_to_string(self, stage):
        return {
            Stage.NONE: 'NaN',
            Stage.SEARCH_FOR_MINERAL: 'Searching for Mineral',
            Stage.COLLECT_MINERAL: 'Collecting Mineral',
            Stage.WEIGH_MINERAL: 'Weighing Mineral',
            Stage.SEARCH_FOR_DEPOSIT_TRAY: 'Searching for Deposit Tray',
            Stage.DEPOSIT_MINERAL_INTO_TRAY: 'Depositing Mineral into Deposit Tray'
        }.get(stage, 'NaN')

    def _socket_send_current_stage(self):
        if self.socket:
            if self.prev_stage != self.current_stage:
                self.socket.send(Constants.JSON_PREFIX.format('{', 'Mineral Analysis', self._stage_to_string(self.current_stage), '', '', '}'))
                self.prev_stage = self.current_stage

    def _send_weight_to_socket(self):
        if self.weighing_count < self.WEIGHING_TIMEOUT:
            self.weighing_count += 1
            self.weights.append(self.rbc.WeightMeasurer.getValue())
            return
        avg_weight = round(sum(self.weights)/len(self.weights),3) if len(self.weights) > 0 else 0
        if self.socket:
            self.socket.send(Constants.JSON_PREFIX.format('{', 'Mineral Analysis', self._stage_to_string(self.current_stage), 'Weight', avg_weight, '}'))
        self.weighing_count = 0
        self.weights = []

    def execute(self, command = False):
        self._socket_send_current_stage()

        if self.current_stage == Stage.SEARCH_FOR_MINERAL:
            if self.mr.get_location_minerals(self.rbc.Camera.getImage()):
                self.current_stage = Stage.COLLECT_MINERAL
                return False
            self._spin()
            return False

        if self.current_stage == Stage.COLLECT_MINERAL:
            if self.cm.execute():
                self.current_stage = Stage.WEIGH_MINERAL
            return False
        
        if self.current_stage == Stage.WEIGH_MINERAL:
            if self.wo.isWeighing():
                self._send_weight_to_socket()
            if self.wo.execute():
                if self.socket:
                    self.socket.send(Constants.JSON_PREFIX.format('{', 'Mineral Analysis', self._stage_to_string(self.current_stage), 'Weight', 0.0, '}'))
                self.current_stage = Stage.SEARCH_FOR_DEPOSIT_TRAY
            return False

        if self.current_stage == Stage.SEARCH_FOR_DEPOSIT_TRAY:
            distance = distance_from_deposit_tray(self.rbc.Camera.getImage(), self.rbc.Camera.getWidth(), self.rbc.Camera.getHeight())
            if distance is not False and distance is not True:
                x,y,distance = distance
            if distance is not False and distance < 100:
                # Found match
                self.current_stage = Stage.DEPOSIT_MINERAL_INTO_TRAY
                return False
            self._spin()
            return False
        
        if self.current_stage == Stage.DEPOSIT_MINERAL_INTO_TRAY:
            # Dew it
            return self.doit.execute()

        return True
    
    def _spin(self):
        self.rbc.turnOnSpot(3)