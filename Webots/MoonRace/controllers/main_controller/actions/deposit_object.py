class DepositObject:
    ARM_REACH_FOR_THE_SKY_INIT_TIME = 164
    arm_reach_for_the_sky_init_time_elapsed = 0

    ARM_EXTEND_TRAVEL_TIME = 164
    arm_extend_travel_time_elapsed = 0

    GRABBER_OPENING_TIME = 64
    grabber_opening_time_elapsed = 0

    ARM_REACH_FOR_THE_SKY_END_TIME = 164
    arm_reach_for_the_sky_end_time_elapsed = 0

    IDLE_TIME = 64
    idle_time_elapsed = 0

    def __init__(self, rbc):
        self.rbc = rbc
    
    def reset(self):
        self.arm_reach_for_the_sky_init_time_elapsed = 0
        self.arm_extend_travel_time_elapsed = 0
        self.grabber_opening_time_elapsed = 0
        self.arm_reach_for_the_sky_end_time_elapsed = 0
        self.idle_time_elapsed = 0

    def execute(self):
        self.rbc.GrabArmMotors.setGrabberVelocity(2)
        self.rbc.GrabArmMotors.setArmVelocity(1)

        if self.arm_reach_for_the_sky_init_time_elapsed < self.ARM_REACH_FOR_THE_SKY_INIT_TIME:
            self.arm_reach_for_the_sky_init_time_elapsed += 1
            self.rbc.GrabArmMotors.arm.reachForTheSky()
            return False

        if self.arm_extend_travel_time_elapsed < self.ARM_EXTEND_TRAVEL_TIME:
            self.arm_extend_travel_time_elapsed += 1
            self.rbc.GrabArmMotors.extendArm_Deposit()
            return False

        if self.grabber_opening_time_elapsed < self.GRABBER_OPENING_TIME:
            self.grabber_opening_time_elapsed += 1
            self.rbc.GrabArmMotors.openGrabber()
            return False
        
        if self.arm_reach_for_the_sky_end_time_elapsed < self.ARM_REACH_FOR_THE_SKY_END_TIME:
            self.arm_reach_for_the_sky_end_time_elapsed += 1
            self.rbc.GrabArmMotors.arm.reachForTheSky()
            return False
        
        if self.idle_time_elapsed < self.IDLE_TIME:
            self.idle_time_elapsed += 1
            self.rbc.GrabArmMotors.idle()
            return False
    
        return True