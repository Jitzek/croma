from vision.deposit_tray_recognition import distance_from_deposit_tray
from actions.deposit_object import DepositObject
from enum import Enum, unique, auto

@unique
class Stages(Enum):
    GO_TO_TRAY = auto()
    DEPOSIT_OBJECT = auto()

class DepositObjectIntoTray:
    current_stage = Stages.GO_TO_TRAY

    def __init__(self, rbc):
        self.rbc = rbc
        self.do = DepositObject(self.rbc)
    
    def reset(self):
        self.current_stage = Stages.GO_TO_TRAY

    def execute(self):
        if self.current_stage == Stages.GO_TO_TRAY:
            distance = distance_from_deposit_tray(self.rbc.Camera.getImage(), self.rbc.Camera.getWidth(), self.rbc.Camera.getHeight())
            if distance is not False and distance is not True:
                x,y,distance = distance
            if distance is True:
                # Destination Reached
                self.current_stage = Stages.DEPOSIT_OBJECT
                return False
            if distance is False:
                return False
            min_x = self.rbc.Camera.getWidth()/2 - self.rbc.Camera.getWidth()/10
            max_x = self.rbc.Camera.getWidth()/2 + self.rbc.Camera.getWidth()/10
            if x < min_x:
                self.rbc.turnOnSpot(-3)
            elif x > max_x:
                self.rbc.turnOnSpot(3)
            else:
                self.rbc.goStraight(3)
            return False
        
        if self.current_stage == Stages.DEPOSIT_OBJECT:
            return self.do.execute()
        
        return True