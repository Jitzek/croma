from vision.obstacle_recognition import ObstacleCourseVision
from vision.avoid_cup import AvoidCup
from enum import Enum, auto, unique

@unique
class Stage(Enum):
    CLIMB_STAIRS = auto()
    #GAP_TRAVERSAL = auto()
    DETECT_GAP = auto()
    
    CALCULATE_ROUTE = auto()

    GO_LEFT_SIDE_1 = auto()
    GO_LEFT_SIDE_2 = auto()
    GO_LEFT_ROUTE_1 = auto()
    GO_LEFT_ROUTE_2 = auto()
    
    GO_RIGHT_SIDE_1 = auto()
    GO_RIGHT_SIDE_2 = auto()
    GO_RIGHT_ROUTE_1 = auto()
    GO_RIGHT_ROUTE_2 = auto()
    
    GO_FORWARD = auto()
    GO_TO_CUP = auto()
    #GO_AROUND_CUP = auto()

class MoonSurvival:
    def __init__(self, rbc, socket=False, vision_display=False):
        self.rbc = rbc
        self.current_stage = Stage.CLIMB_STAIRS
        self.ocv = ObstacleCourseVision(self.rbc.Camera)
        self.ac = AvoidCup(rbc.Robot, rbc.Camera)
    
    def reset(self):
        self.current_stage = Stage.CLIMB_STAIRS

    """
        TODO: Refactor code, vision files shouldn't contain movement logic
        GAP_TRAVERSAL Refactor: DONE by Micky
    """
    def execute(self, command = False):
        print(self.current_stage)

        self.ocv.refreshVisionData()
        
        # LEGEND:
        # @ = location of robot
        
        # _____________________
        #|\ramp with coffee cup\
        #| \____________________\
        #| |      platform      | 
        #|_|_____          _____| 
        #  gap| | bridge | gap     
        # _ __|_|        |______
        #| |      platform      |
        #| |____________________|
        #| /      stairs       /
        #|/___________________/    
        #
        #    @  or  @  or @

        # center robot by centering the stairs in camera image
        # and go straight
        if self.current_stage == Stage.CLIMB_STAIRS:
            centerX = self.ocv.get_pos_stairs()
            if centerX is True:
                self.current_stage = Stage.DETECT_GAP
                return False
            if centerX < self.rbc.Camera.getWidth()/2 - 2:
                self.rbc.turnOnSpot(-2)
                return False
            if centerX > self.rbc.Camera.getWidth()/2 + 2: 
                self.rbc.turnOnSpot(2)
                return False
            self.rbc.goStraight(5)
            return False
        
        

        # LEGEND:
        # @ = location of robot

        # robot orientation: NORTH
        # _____________________
        #|\ramp with coffee cup\
        #| \____________________\
        #| |      platform      | 
        #|_|_____          _____| 
        # gap | | bridge | gap     
        # ____|_|        |______
        #|  |      platform     |
        #|  |                   | 
        #|  |__________________ |
        #|  /      stairs       /
        #| / @ or @ or @ or @  /
        #|/___________________/
        
        # detect the gap   
        if self.current_stage == Stage.DETECT_GAP:
            self.rbc.goStraight(5)
            if self.ocv.getIsGapDetected() is True:
                self.current_stage = Stage.CALCULATE_ROUTE
            return False
        
        # LEGEND:
        # @ = location of robot

        #robot orientation: NORTH
        # _____________________
        #|\ramp with coffee cup\
        #| \____________________\
        #| |      platform      | 
        #|_|_____          _____| 
        # gap | | bridge | gap     
        # _ __|_|        |______
        #| |      platform      |
        #| |                    | 
        #| | @ or @ or @ or @   | 
        #| |____________________|
        #| /      stairs       /
        #|/___________________/
        
        # calculate route by gap distance(perimeter get bigger when closer) and bridge position(left or right)
        if self.current_stage == Stage.CALCULATE_ROUTE:
            self.rbc.goStraight(5)
            perimeter, leftPos, rightPos = self.ocv.getBridgeStats()
            print(perimeter)
            if perimeter > 105 and rightPos > leftPos:
                self.current_stage = Stage.GO_LEFT_SIDE_1
            if perimeter > 105 and leftPos > rightPos:
                self.current_stage = Stage.GO_RIGHT_SIDE_1
            return False

        # LEGEND:
        # @ = location of robot

        #robot orientation: NORTH
        # _____________________
        #|\ramp with coffee cup\
        #| \____________________\
        #| |      platform      | 
        #|_|_____          _____| 
        # gap | | bridge | gap     
        # _ __|_|        |______
        #| |      platform      |
        #| | @ or @ or @ or @   |
        #| |                    | 
        #| |____________________|
        #| /      stairs       /
        #|/___________________/

        ################################LEFT ROUTE#####################################
        
        # turn left until gap box is touches right side of camera image
        if self.current_stage == Stage.GO_LEFT_SIDE_1:
            self.turnLeft()
            x,y,w,h = self.ocv.getGapBoxMeasurements()
            if (x+w) == self.rbc.Camera.getWidth():
                self.current_stage = Stage.GO_LEFT_SIDE_2
            return False

        # LEGEND:
        # @ = location of robot

        #robot orientation: NORTHWEST-ISH
        # _____________________
        #|\ramp with coffee cup\
        #| \____________________\
        #| |      platform      | 
        #|_|_____          _____| 
        # gap | | bridge | gap     
        # _ __|_|        |______
        #| |      platform      |
        #| | @ or @             |
        #| |                    |
        #| |____________________|
        #| /      stairs       /
        #|/___________________/
        
        # go some time straight until somewhat closer to gap box(gap is lower in camera image)
        if self.current_stage == Stage.GO_LEFT_SIDE_2:
            self.rbc.goStraight(5)
            x,y,w,h = self.ocv.getGapBoxMeasurements()
            if y > 98:
                self.current_stage = Stage.GO_LEFT_ROUTE_1
            return False

        #robot orientation: NORTHWEST-ISH
        # _____________________
        #|\ramp with coffee cup\
        #| \____________________\
        #| |      platform      | 
        #|_|_____          _____| 
        # gap | | bridge | gap     
        # _ __|_|        |______
        #| | @ or @ platform    |
        #| |                    |
        #| |                    |
        #| |____________________|
        #| /      stairs       /
        #|/___________________/

        # position reached for taking of from left route, now reach for the gap
        # movement is determined by amount of gap boxes detected on camera image
        # turn right until camera is facing the bridge
        # then go straight until camera is close(gap is lower in camera image) to the bridge
        if self.current_stage == Stage.GO_LEFT_ROUTE_1:
            box_array = self.ocv.getGapBoxes()
            if len(box_array) == 1:
                self.turnRight()
            if len(box_array) == 2:
                self.goStraight()
                
                min = 256
                for box in box_array:            
                    if box[1] < min:
                        min = box[1]
           
                if min > self.rbc.Camera.getHeight()/2:
                    self.current_stage = Stage.GO_LEFT_ROUTE_2
            return False
        # LEGEND:
        # @ = location of robot
        
        #robot orientation: NORTHEAST-ISH
        # _____________________
        #|\ramp with coffee cup\
        #| \____________________\
        #| |      platform      | 
        #|_|_____          _____| 
        # gap | | bridge | gap     
        # _ __|_|        |______
        #| |       @ platform   |
        #| |                    |
        #| |                    |
        #| |____________________|
        #| /      stairs       /
        #|/___________________/
        
        #turn left until centered, then traverse the gap
        if self.current_stage == Stage.GO_LEFT_ROUTE_2:
            self.turnLeft()
            if self.ocv.robotIsCentered() == True:
                self.current_stage = Stage.GO_FORWARD
            return False
        ################################################################################
        
        ################################RIGHT ROUTE#####################################
        # turn right until gap box is touches left side of camera image
        if self.current_stage == Stage.GO_RIGHT_SIDE_1:
            self.turnRight()
            x,y,w,h = self.ocv.getGapBoxMeasurements()
            if x == 0:
                self.current_stage = Stage.GO_RIGHT_SIDE_2
            return False

        # LEGEND:
        # @ = location of robot
        
        #robot orientation: NORTHEAST-ISH
        # _____________________
        #|\ramp with coffee cup\
        #| \____________________\
        #| |      platform      | 
        #|_|_____          _____| 
        # gap | | bridge | gap     
        # _ __|_|        |______
        #| |    platform        |
        #| |                    |
        #| |           @  or  @ |
        #| |____________________|
        #| /      stairs       /
        #|/___________________/

        # go some time straight until somewhat closer to gap box(gap is lower in camera image)
        if self.current_stage == Stage.GO_RIGHT_SIDE_2:
            self.rbc.goStraight(5)
            x,y,w,h = self.ocv.getGapBoxMeasurements()
            if y > 98:
                self.current_stage = Stage.GO_RIGHT_ROUTE_1
            return False

        # LEGEND:
        # @ = location of robot
        
        #robot orientation: NORTHEAST-ISH
        # _____________________
        #|\ramp with coffee cup\
        #| \____________________\
        #| |      platform      | 
        #|_|_____          _____| 
        # gap | | bridge | gap     
        # _ __|_|        |______
        #| |    platform        |
        #| |          @  or  @  |
        #| |                    |
        #| |____________________|
        #| /      stairs       /
        #|/___________________/

        # position reached for taking of from right route, now reach for the gap
        # movement is determined by amount of gap boxes detected on camera image
        # turn left until camera is facing the bridge
        # then go straight until camera is close(gap is lower in camera image) to the bridge
        if self.current_stage == Stage.GO_RIGHT_ROUTE_1:
            box_array = self.ocv.getGapBoxes()
            if len(box_array) == 1:
                self.turnLeft()
            if len(box_array) == 2:
                self.goStraight()
                
                min = 256
                for box in box_array:            
                    if box[1] < min:
                        min = box[1]
           
                if min > self.rbc.Camera.getHeight()/2:
                    self.current_stage = Stage.GO_RIGHT_ROUTE_2
            return False

        #robot orientation: NORTHWEST-ISH
        # _____________________
        #|\ramp with coffee cup\
        #| \____________________\
        #| |      platform      | 
        #|_|_____          _____| 
        # gap | | bridge | gap     
        # _ __|_|        |______
        #| | platform @         |
        #| |                    |
        #| |                    |
        #| |____________________|
        #| /      stairs       /
        #|/___________________/

        #turn right until centered, then traverse the gap
        if self.current_stage == Stage.GO_RIGHT_ROUTE_2:
            self.turnRight()
            if self.ocv.robotIsCentered() == True:
                self.current_stage = Stage.GO_FORWARD
            return False

        
        ################################################################################

        #robot orientation: NORTH
        # _____________________
        #|\ramp with coffee cup\
        #| \____________________\
        #| |      platform      | 
        #|_|_____          _____| 
        # gap | | bridge | gap     
        # _ __|_|        |______
        #| | platform @         |
        #| |                    |
        #| |                    |
        #| |____________________|
        #| /      stairs       /
        #|/___________________/
            
        if self.current_stage == Stage.GO_FORWARD:
            if self.ac.vision.isCupSeen(self.rbc.Camera):
                self.current_stage = Stage.GO_TO_CUP
                return False
            self.rbc.goStraight(5)
            return False
        # LEGEND:
        # @ = location of robot
        
        #robot orientation: NORTH
        # _____________________
        #|\ramp with coffee cup\
        #| \         @          \
        #|  \        or          \
        #|   \____________________\
        #|   |      platform      |
        #|   |         @          |
        #|   |         or         |
        #|___|_____          _____| 
        # gap    | | bridge | gap
        #        | |   @    |
        # _______|_|        |_____
        #|   |    platform        |
        #|   |                    |
        #|   |                    |
        #|   |____________________|
        #|  /      stairs         /
        #| /                     /
        #|/_____________________/
        if self.current_stage == Stage.GO_TO_CUP:
            print(self.ac.touchedBool)
            self.ac.execute()
            return False

        return True
    
    def goStraight(self):
        self.rbc.RightWheelMotors.setVelocities(-5,-5,0)
        self.rbc.LeftWheelMotors.setVelocities(5,5,0)
        
    def turnLeft(self):
        self.rbc.RightWheelMotors.setVelocities(-3,-3,0)
        self.rbc.LeftWheelMotors.setVelocities(-3,-3,0)

    def turnRight(self):
        self.rbc.RightWheelMotors.setVelocities(3,3,0)
        self.rbc.LeftWheelMotors.setVelocities(3,3,0)

