from vision.obstacle_recognition import ObstacleCourseVision
from vision.avoid_cup import AvoidCup
from enum import Enum, auto, unique

@unique
class Stage(Enum):
    CLIMB_STAIRS = auto()
    GAP_TRAVERSAL = auto()
    GO_FORWARD = auto()
    GO_TO_CUP = auto()
    GO_AROUND_CUP = auto()

class MoonSurvival:
    def __init__(self, rbc, socket=False, vision_display=False):
        self.rbc = rbc
        self.current_stage = Stage.CLIMB_STAIRS
        self.ocv = ObstacleCourseVision(self.rbc)
        self.ac = AvoidCup(rbc.Robot, rbc.Camera)
    
    def reset(self):
        self.current_stage = Stage.CLIMB_STAIRS

    """
        TODO: Refractor code, vision shouldn't contain movement logic
    """
    def execute(self, command = False):
        print(self.current_stage)
        if self.current_stage == Stage.CLIMB_STAIRS:
            centerX = self.ocv.get_pos_stairs()
            if centerX is True:
                self.current_stage = Stage.GAP_TRAVERSAL
                return False
            if centerX < self.rbc.Camera.getWidth()/2 - 2:
                self.rbc.turnOnSpot(-2)
                return False
            if centerX > self.rbc.Camera.getWidth()/2 + 2: 
                self.rbc.turnOnSpot(2)
                return False
            self.rbc.goStraight(5)
            return False
        if self.current_stage == Stage.GAP_TRAVERSAL:
            if self.ocv.go_over_gap() is True:
                self.current_stage = Stage.GO_FORWARD
            return False
        if self.current_stage == Stage.GO_FORWARD:
            if self.ac.vision.isCupSeen(self.rbc.Camera):
                self.current_stage = Stage.GO_TO_CUP
                return False
            self.rbc.goStraight(3)
            return False
        if self.current_stage == Stage.GO_TO_CUP:
            print(self.ac.touchedBool)
            self.ac.execute()
            return False

        return True