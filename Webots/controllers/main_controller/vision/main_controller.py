"""main_controller controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot,Camera,Motor,Display

import sys
from avoid_cup import AvoidCup

# Get the robot      
robot = Robot()
timestep = int(robot.getBasicTimeStep() * 4)

camera = Camera("camera")
camera.enable(timestep)

AvoidCup = AvoidCup(robot,camera)

while robot.step(timestep) != -1:
    AvoidCup.execute()
    