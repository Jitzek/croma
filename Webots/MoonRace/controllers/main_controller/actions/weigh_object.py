import Constants

class WeighObject:
    ARM_TRAVEL_TIME = 164
    arm_travel_time_elapsed = 0

    GRABBER_OPENING_TIME = 64
    grabber_opening_time_elapsed = 0

    WEIGHING_TIME = 256
    weighing_time_elapsed = 0

    GRABBER_CLOSING_TIME = 64
    grabber_closing_time_elapsed = 0

    ARM_REACH_FOR_THE_SKY_TIME = 64
    arm_reach_for_the_sky_elapsed = 0

    def __init__(self, rbc):
        self.rbc = rbc
    
    def isWeighing(self):
        return self.weighing_time_elapsed > 0 and self.weighing_time_elapsed < self.WEIGHING_TIME
    
    def reset(self):
        self.arm_travel_time_elapsed = 0
        self.grabber_opening_time_elapsed = 0
        self.weighing_time_elapsed = 0
        self.grabber_closing_time_elapsed = 0
        self.arm_reach_for_the_sky_elapsed = 0

    def execute(self):
        self.rbc.GrabArmMotors.setGrabberVelocity(2)
        self.rbc.GrabArmMotors.setArmVelocity(1)

        if self.arm_travel_time_elapsed < self.ARM_TRAVEL_TIME:
            self.arm_travel_time_elapsed += 1
            self.rbc.GrabArmMotors.goToWeighPos()
            return False

        if self.grabber_opening_time_elapsed < self.GRABBER_OPENING_TIME:
            self.grabber_opening_time_elapsed += 1
            self.rbc.GrabArmMotors.openGrabber()
            return False
        
        if self.weighing_time_elapsed < self.WEIGHING_TIME:
            self.weighing_time_elapsed += 1
            return False
        
        if self.grabber_closing_time_elapsed < self.GRABBER_CLOSING_TIME:
            self.grabber_closing_time_elapsed += 1
            self.rbc.GrabArmMotors.closeGrabber()
            return False
        
        if self.arm_reach_for_the_sky_elapsed < self.ARM_REACH_FOR_THE_SKY_TIME:
            self.arm_reach_for_the_sky_elapsed += 1
            self.rbc.GrabArmMotors.arm.reachForTheSky()
            return False

        self.rbc.GrabArmMotors.idle()
        
    
        return True