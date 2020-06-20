from vision.deposit_tray_recognition import distance_from_deposit_tray
from actions.deposit_object_into_tray import DepositObjectIntoTray
from enum import Enum, unique, auto

@unique
class Stage(Enum):
    SEARCH_FOR_TRAY = auto()
    GO_TO_TRAY = auto()
    DEPOSIT_OBJECT = auto()

class SearchAndDepositIntoTray:
    current_stage = Stage.GO_TO_TRAY

    def __init__(self, rbc):
        self.rbc = rbc
        self.doit = DepositObjectIntoTray(self.rbc)
    
    def reset(self):
        self.current_stage = Stage.GO_TO_TRAY
        self.doit.reset()

    def execute(self):
        if self.current_stage == Stage.SEARCH_FOR_TRAY:
            distance = distance_from_deposit_tray(self.rbc.Camera.getImage(), self.rbc.Camera.getWidth(), self.rbc.Camera.getHeight())
            if distance is not False and distance is not True:
                x,y,distance = distance
            if distance is not False and distance < 100:
                # Found match
                self.current_stage = Stage.GO_TO_TRAY
                return False
            self.rbc.turnOnSpot(3)


        if self.current_stage == Stage.GO_TO_TRAY:
            distance = distance_from_deposit_tray(self.rbc.Camera.getImage(), self.rbc.Camera.getWidth(), self.rbc.Camera.getHeight())
            if distance is not False and distance is not True:
                x,y,distance = distance
            if distance is True:
                # Destination Reached
                self.current_stage = Stage.DEPOSIT_OBJECT
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
        
        if self.current_stage == Stage.DEPOSIT_OBJECT:
            # dew it
            return self.doit.execute()
        
        return True