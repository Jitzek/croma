from vision.mineral_recognition import MineralRecognition, DistanceFromMineral, MineralFlags as mf
from enum import Enum, unique, auto
from actions.grab_object import GrabObject

class Stage(Enum):
    GO_TO_MINERAL = auto()
    PICK_UP_MINERAL = auto()
    WEIGH_MINERAL = auto()

class CollectMineral:
    MAXIMUM_DISTANCE = 0.1
    MINIMUM_DISTANCE = 0.01

    def __init__(self, rbc):
        self.rbc = rbc
        self.mr = MineralRecognition(self.rbc.Camera)
        self.dfm = DistanceFromMineral(self.rbc.Camera.getWidth(), self.rbc.Camera.getHeight(), 0.095)
        self.current_stage = Stage.GO_TO_MINERAL
        self.grab_object = GrabObject(self.rbc)

    def reset(self):
        self.current_stage = Stage.GO_TO_MINERAL
        self.grab_object.reset()

    def execute(self):
        data = self.mr.get_location_minerals(self.rbc.Camera.getImage())
        
        largest_match = self.mr.get_largest_location(data)
        if not largest_match:
            return False
        
        if self.current_stage == Stage.GO_TO_MINERAL:
            distance = self.dfm.getDistance(largest_match[2], largest_match[3], largest_match[4])
            if self.goToPosition(largest_match[0] + largest_match[2]/2, distance, largest_match[4]):
                self.current_stage = Stage.PICK_UP_MINERAL
            return False
        
        if self.current_stage == Stage.PICK_UP_MINERAL:
            if not self.grab_object.execute():
                return False
        
        return True

    def goToPosition(self, x, distance, flag):
        X_DEV = int(self.rbc.Camera.getWidth()/10)

        max_x = self.rbc.Camera.getWidth()
        print(distance,max_x)
        if x < (max_x/2) - X_DEV:
            self.rbc.turnOnSpot(-3)
            return False
        if x > (max_x/2) + X_DEV:
            self.rbc.turnOnSpot(3)
            return False
        if flag == mf.BIG:
            if distance < self.MINIMUM_DISTANCE:
                self.rbc.goStraight(-3)
                return False
            if distance > self.MAXIMUM_DISTANCE:
                self.rbc.goStraight(3)
                return False
        if flag == mf.SMALL:
            if distance < self.MINIMUM_DISTANCE:
                self.rbc.goStraight(-3)
                return False
            if distance > self.MAXIMUM_DISTANCE:
                self.rbc.goStraight(3)
                return False
        return True