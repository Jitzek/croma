
class DancingOnTheMoon:
    '''
        Note:
        I did not enjoy making this, nor am I proud of it
    '''

    # MADE FOR BASIC TIMESTEP == 8

    # Beat ~= 48 iterations

    # Intro head bobbing
    INTRO_TIME = 1224
    intro_count = 0
    HEAD_BOB_TIME = 32
    head_bob_count = 0
    HEAD_BOB_RETURN_TIME = 16
    head_bob_return_count = 0
    head_bob = True
    head_bob_return = False

    # Beat break
    BREAK_BEFORE_DROP_TIME = 192
    break_before_drop_count = 0
    BB_TURN_LEFT_TIME = 12
    bb_turn_left_count = 0
    BB_TURN_RIGHT_TIME = 48
    bb_turn_right_count = 0
    BB_RIGHT_TO_BACKWARDS_WAIT_TIME = 52
    bb_right_to_backwards_wait_count = 0
    BB_BACKWARDS_TIME = 128
    bb_backwards_count = 0

    # Drop 1
    DROP1_TIME = 2448
    drop2_count = 0
    D1_SPEED_UP_FORWARDS_TIME = 248
    d1_speed_up_forwards = 0
    D1_BRAKE_TIME = 128
    d1_brake_count = 0
    D1_SPEEEN_TIME = 128
    d1_speeen_count = 0
    D1_GO_FORWARDS_TIME = 64
    d1_go_forwards_count = 0
    D1_SPEEEN_ON_GROUND_TIME = 192
    d1_speeen_on_ground_count = 0
    D1_SPEEEN_ON_GROUND_RETRACT_ARM_TIME = 378
    d1_speeen_on_ground_retract_arm_count = 0
    D1_SPEEEN_ON_GROUND_REVERSE_TIME = 378
    d1_speen_on_ground_reverse_count = 0


    
    BRIDGE_TIME = 2778
    bridge_count = 0

    # Drop 2
    DROP2_TIME = 2448
    drop2_count = 0
    D2_SPEED_UP_FORWARDS_TIME = 200
    d2_speed_up_forwards = 0
    D2_BRAKE_TIME = 128
    d2_brake_count = 0
    D2_SPEEEN_TIME = 128
    d2_speeen_count = 0
    D2_SPEEEN_ON_GROUND_TIME = 64
    d2_speeen_on_ground_count = 0
    D2_GO_FORWARDS_TIME = 64
    d2_go_forwards_count = 0
    D2_SPEEEN_ON_GROUND_RETRACT_ARM_TIME = 378
    d2_speeen_on_ground_retract_arm_count = 0
    D2_SPEEEN_ON_GROUND_REVERSE_TIME = 378
    d2_speen_on_ground_reverse_count = 0

    D2_SHUFFLE_AND_ARM_TIME = 256
    d2_shuffle_and_arm_count = 0
    D2_SAA_TIME = 24
    d2_saa_count = 0
    d2_saa_forwards = True
    d2_saa_backwards = False

    intro = True
    drop1 = False
    bridge = False
    drop2 = False

    def __init__(self, rbc, socket=False, vision_display=False):
        self.rbc = rbc
    
    def reset(self):
        pass
        
    def execute(self, command = False):
        if self.intro:
            self._intro()
            return False
        if self.drop1:
            self._drop1()
            return False
        if self.bridge:
            self._bridge()
            return False
        if self.drop2:
            self._drop2()
            return False
        return True

    
    def _intro(self):
        if self.intro_count < self.INTRO_TIME:
            self._bop_head()
            self.intro_count += 1
            return False
        if self.bb_turn_left_count < self.BB_TURN_LEFT_TIME:
            self.rbc.turnOnSpot(self.rbc.LeftWheelMotors.getMaxVelocity() *- 1)
            self.bb_turn_left_count += 1
            return False
        if self.bb_turn_right_count < self.BB_TURN_RIGHT_TIME:
            self.rbc.turnOnSpot(self.rbc.LeftWheelMotors.getMaxVelocity())
            self.bb_turn_right_count += 1
            return False
        if self.bb_right_to_backwards_wait_count < self.BB_RIGHT_TO_BACKWARDS_WAIT_TIME:
            self.bb_right_to_backwards_wait_count += 1
            return False
        if self.bb_backwards_count < self.BB_BACKWARDS_TIME:
            self.rbc.goStraight(self.rbc.LeftWheelMotors.getMaxVelocity() * -1)
            self.bb_backwards_count += 1
            return False
        
        self.intro = False
        self.drop1 = True
        return True

    def _drop1(self):
        if self.d1_speed_up_forwards < self.D1_SPEED_UP_FORWARDS_TIME:
            self.rbc.goStraight(self.rbc.LeftWheelMotors.getMaxVelocity())
            self.d1_speed_up_forwards += 1
            return False

        if self.d1_brake_count < self.D1_BRAKE_TIME:
            self.rbc.goStraight(self.rbc.LeftWheelMotors.getMaxVelocity() * -1)
            self.d1_brake_count += 1
            return False
        
        if self.d1_speeen_count < self.D1_SPEEEN_TIME:
            self.rbc.extendArm(1, self.rbc.GrabArmMotors.arm.getMaxVelocity())
            self.rbc.openGrabber(self.rbc.GrabArmMotors.grabber.getMaxVelocity())
            self.rbc.turnOnSpot(self.rbc.LeftWheelMotors.getMaxVelocity())
            self.d1_speeen_count += 1
            return False
            
        if self.d1_go_forwards_count < self.D1_GO_FORWARDS_TIME:
            self.rbc.retractArm(1, self.rbc.GrabArmMotors.arm.getMaxVelocity())
            self.rbc.closeGrabber(self.rbc.GrabArmMotors.grabber.getMaxVelocity())
            self.rbc.goStraight(self.rbc.LeftWheelMotors.getMaxVelocity()/2)
            self.d1_go_forwards_count += 1
            return False
            
        if self.d1_speeen_on_ground_count < self.D1_SPEEEN_ON_GROUND_TIME:
            self.rbc.GrabArmMotors.setArmVelocity(self.rbc.GrabArmMotors.arm.getMaxVelocity()/2)
            self.rbc.GrabArmMotors.setGrabberVelocity(self.rbc.GrabArmMotors.grabber.getMaxVelocity()/2)
            self.rbc.GrabArmMotors.idle()
            self.rbc.turnOnSpot(self.rbc.LeftWheelMotors.getMaxVelocity()/2)
            self.d1_speeen_on_ground_count += 1
            return False
            
        if self.d1_speeen_on_ground_retract_arm_count < self.D1_SPEEEN_ON_GROUND_RETRACT_ARM_TIME:
            self.rbc.GrabArmMotors.retract()
            self.rbc.turnOnSpot(self.rbc.LeftWheelMotors.getMaxVelocity()/2)
            self.d1_speeen_on_ground_retract_arm_count += 1
            return False
        
        if self.d1_speen_on_ground_reverse_count < self.D1_SPEEEN_ON_GROUND_REVERSE_TIME:
            self.rbc.GrabArmMotors.idle()
            self.rbc.turnOnSpot((self.rbc.LeftWheelMotors.getMaxVelocity()/2)*-1)
            self.d1_speen_on_ground_reverse_count += 1
            return False

        self.head_bobbing_count = 0
        self.drop1 = False
        self.bridge = True
        return True

    def _bop_head(self):
        self.rbc.setGrabberMotorVelocity(self.rbc.GrabArmMotors.grabber.getMaxVelocity())
        self.rbc.setArmMotorVelocity(self.rbc.GrabArmMotors.arm.getMaxVelocity())
        if self.head_bob:
            if self.head_bob_count < self.HEAD_BOB_TIME:
                self.head_bob_count += 1
                return
            self.rbc.GrabArmMotors.grabber.setPositionOfMotor(self.rbc.GrabArmMotors.grabber.grabber_full, 1.3)
            # bop head forwards
            self.head_bob_count = 0
            self.head_bob_return = True
            self.head_bob = False
            return
        if self.head_bob_return_count < self.HEAD_BOB_RETURN_TIME:
            self.head_bob_return_count += 1
            return
        self.rbc.GrabArmMotors.grabber.setPositionOfMotor(self.rbc.GrabArmMotors.grabber.grabber_full, 1.0)
        # bop head backwards
        self.head_bob_return_count = 0
        self.head_bob_return = False
        self.head_bob = True
    
    def _bridge(self):
        if self.bridge_count < self.BRIDGE_TIME:
            self._bop_head()
            self.bridge_count += 1
            return False
        self.bridge = False
        self.drop2 = True
        return True
    
    def _drop2(self):
        if self.d2_speed_up_forwards < self.D2_SPEED_UP_FORWARDS_TIME:
            self.rbc.goStraight(self.rbc.LeftWheelMotors.getMaxVelocity() - 2)
            self.d2_speed_up_forwards += 1
            return False

        if self.d2_brake_count < self.D2_BRAKE_TIME:
            self.rbc.goStraight(self.rbc.LeftWheelMotors.getMaxVelocity() * -1)
            self.d2_brake_count += 1
            return False
        
        if self.d2_speeen_count < self.D2_SPEEEN_TIME:
            self.rbc.extendArm(1, self.rbc.GrabArmMotors.arm.getMaxVelocity())
            self.rbc.openGrabber(self.rbc.GrabArmMotors.grabber.getMaxVelocity())
            self.rbc.turnOnSpot(self.rbc.LeftWheelMotors.getMaxVelocity())
            self.d2_speeen_count += 1
            return False
        
        if self.d2_speeen_on_ground_count < self.D2_SPEEEN_ON_GROUND_TIME:
            self.rbc.GrabArmMotors.setArmVelocity(self.rbc.GrabArmMotors.arm.getMaxVelocity()/2)
            self.rbc.GrabArmMotors.setGrabberVelocity(self.rbc.GrabArmMotors.grabber.getMaxVelocity()/2)
            self.rbc.GrabArmMotors.idle()
            self.rbc.turnOnSpot(self.rbc.LeftWheelMotors.getMaxVelocity()/2)
            self.d2_speeen_on_ground_count += 1
            return False
        
        if self.d2_go_forwards_count < self.D2_GO_FORWARDS_TIME:
            self.rbc.retractArm(1, self.rbc.GrabArmMotors.arm.getMaxVelocity())
            self.rbc.closeGrabber(self.rbc.GrabArmMotors.grabber.getMaxVelocity())
            self.rbc.goStraight(self.rbc.LeftWheelMotors.getMaxVelocity()/2)
            self.d2_go_forwards_count += 1
            return False
            
        if self.d2_speeen_on_ground_retract_arm_count < self.D2_SPEEEN_ON_GROUND_RETRACT_ARM_TIME:
            self.rbc.GrabArmMotors.retract()
            self.rbc.turnOnSpot(self.rbc.LeftWheelMotors.getMaxVelocity()/2)
            self.d2_speeen_on_ground_retract_arm_count += 1
            return False
        
        if self.d2_speen_on_ground_reverse_count < self.D2_SPEEEN_ON_GROUND_REVERSE_TIME:
            self.rbc.GrabArmMotors.idle()
            self.rbc.turnOnSpot((self.rbc.LeftWheelMotors.getMaxVelocity()/2)*-1)
            self.d2_speen_on_ground_reverse_count += 1
            return False
        
        if self.d2_shuffle_and_arm_count < self.D2_SHUFFLE_AND_ARM_TIME:
            self.d2_shuffle_and_arm_count += 1
            if self.d2_saa_forwards:
                if self.d2_saa_count < self.D2_SAA_TIME:
                    self.rbc.goStraight(self.rbc.LeftWheelMotors.getMaxVelocity()/2)
                    self.d2_saa_count += 1
                    return False
                self.d2_saa_forwards = False
                self.d2_saa_backwards = True
                self.d2_saa_count = 0
            if self.d2_saa_backwards:
                if self.d2_saa_count < self.D2_SAA_TIME:
                    self.rbc.goStraight((self.rbc.LeftWheelMotors.getMaxVelocity()/2) *-1)
                    self.d2_saa_count += 1
                    return False
                self.d2_saa_forwards = True
                self.d2_saa_backwards = False
                self.d2_saa_count = 0


        self.head_bobbing_count = 0
        self.drop2 = False
        self.bridge = True
        return True