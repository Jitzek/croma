class GrabObject:
    ARM_EXTENSION_TIME = 96
    grabber_opening_time_elapsed = 0

    GRABBER_CLOSING_TIME = 96
    grabber_closing_time_elapsed = 0

    IDLE_TIME = 164
    idle_time_elapsed = 0

    def __init__(self, rbc):
        self.rbc = rbc
    
    def reset(self):
        self.arm_extension_time_elapsed = 0
        self.grabber_closing_time_elapsed = 0
        self.idle_time_elapsed = 0

    def execute(self):
        self.rbc.GrabArmMotors.setGrabberVelocity(3)
        self.rbc.GrabArmMotors.setArmVelocity(3)

        if self.arm_extension_time_elapsed < self.ARM_EXTENSION_TIME:
            self.arm_extension_time_elapsed += 1
            self.rbc.openGrabber(3)
            self.rbc.GrabArmMotors.extendArm_Grab()
            return False
    
        if (self.grabber_closing_time_elapsed < self.GRABBER_CLOSING_TIME):
            self.grabber_closing_time_elapsed += 1
            self.rbc.closeGrabber(3)
            return False
        
        if (self.idle_time_elapsed < self.IDLE_TIME):
            self.idle_time_elapsed += 1
            self.rbc.idle()
            return False
    
        return True


