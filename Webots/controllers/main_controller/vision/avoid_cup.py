from vision.drive_to_cup import DriveToCup
from vision.coffee_cup_vision import CoffeeCupVision

from enum import Enum, auto, unique

@unique
class Stage(Enum):
    CUP_NOT_FOUND = auto()
    DRIVE_TOWARD_CUP = auto()
    REVERSING_FROM_CUP = auto()
    FINDING_EDGE = auto()
    DRIVE_TOWARD_EDGE = auto()
    FIND_ALIGNMENT_EDGE = auto()
    DRIVE_ALONG_EDGE = auto()


class AvoidCup:
    current_mission = Stage.CUP_NOT_FOUND
    touchedBool = False
    reachedAlignment = False
    alignment = "not align"

    def __init__(self, robot, camera):
        self.robot = robot
        self.camera = camera
        self.dtc = DriveToCup(robot)
        self.vision = CoffeeCupVision(camera, robot)

    def execute(self):
        if self.touchedBool is False and not self.reachedAlignment:
            self.touchedBool = self.vision.see_cup(self.camera.getImage(), self.camera)
        elif self.touchedBool is True and self.alignment == "not align" and not self.reachedAlignment:
            self.alignment = self.vision.avoid_cup(self.camera.getImage(), self.camera)
        elif self.touchedBool is True and self.alignment == "align" and not \
                self.vision.alignWithEdge(self.camera.getImage, self.camera) and not self.reachedAlignment:
            self.vision.alignWithEdge(self.camera.getImage(), self.camera)
        else:
            self.reachedAlignment = True
            self.dtc.forward(2)
