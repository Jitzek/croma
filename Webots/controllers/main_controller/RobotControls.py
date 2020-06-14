class WheelMotors:
    def __init__(self, wheels):
        self.wheels = wheels
        for wheel in wheels:
            wheel.setPosition(float('inf'))
        self.velocity = 0
        self.setVelocity(self.velocity)
    
    def getMaxVelocity(self):
        max_velocity = 0
        for wheel in self.wheels:
            if wheel.getMaxVelocity() > max_velocity:
                max_velocity = wheel.getMaxVelocity()
        return max_velocity
    
    def getVelocity(self):
        return self.velocity
    
    def setVelocity(self, velocity):
        if abs(velocity) > self.getMaxVelocity():
            return
        for wheel in self.wheels:
            wheel.setVelocity(velocity)
        self.velocity = velocity
    

class Arm:
    arm_full_position = 0
    arm_center_position = 0
    velocity = 3

    ARM_FULL_EXTENDED = -1
    ARM_CENTER_EXTENDED = 1

    ARM_FULL_RETRACTED = 1.25
    ARM_CENTER_RETRACTED = -0.75

    ARM_FULL_SKY = 0.5
    ARM_CENTER_SKY = 0

    ARM_FULL_IDLE_POS = 1.5
    ARM_CENTER_IDLE_POS = 2

    ARM_FULL_STEP_EXTENDING = 0.01
    ARM_CENTER_STEP_EXTENDING = 0.025

    ARM_FULL_STEP_RETRACTING = 0.025
    ARM_CENTER_STEP_RETRACTING = 0.01

    ARM_FULL_WEIGH_POS = 0.65
    ARM_CENTER_WEIGH_POS = -0.1

    def __init__(self, arm_full, arm_center):
        self.arm_full = arm_full
        self.arm_center = arm_center
        self.motors = [self.arm_full, self.arm_center]
        self.setVelocity(self.velocity)
    
    def idle(self):
        self.setPositionOfMotor(self.arm_full, self.ARM_FULL_IDLE_POS)
        self.setPositionOfMotor(self.arm_center, self.ARM_CENTER_IDLE_POS)

    def extend_Grab(self):
        self.setPositionOfMotor(self.arm_full, self.ARM_FULL_EXTENDED)
        self.setPositionOfMotor(self.arm_center, self.ARM_CENTER_EXTENDED)
    
    def extend_Deposit(self):
        self.setPositionOfMotor(self.arm_full, self.ARM_FULL_EXTENDED + self.ARM_FULL_STEP_RETRACTING*20)
        self.setPositionOfMotor(self.arm_center, self.ARM_CENTER_EXTENDED)
    
    def retract(self):
        self.setPositionOfMotor(self.arm_full, self.ARM_FULL_RETRACTED)
        self.setPositionOfMotor(self.arm_center, self.ARM_CENTER_RETRACTED)
    
    def reachForTheSky(self):
        self.setPositionOfMotor(self.arm_full, self.ARM_FULL_SKY)
        self.setPositionOfMotor(self.arm_center, self.ARM_CENTER_SKY)
    
    def isExtended(self):
        return self.arm_full_position == self.ARM_FULL_EXTENDED and self.arm_center_position == self.ARM_CENTER_EXTENDED
    
    def isRetracted(self):
        return self.arm_full_position == self.ARM_FULL_RETRACTED and self.arm_center_position == self.ARM_CENTER_RETRACTED

    def goToWeighPos(self):
        self.arm_full_position = self.ARM_FULL_WEIGH_POS
        self.arm_center_position = self.ARM_CENTER_WEIGH_POS
        self.setPositionOfMotor(self.arm_full, self.arm_full_position)
        self.setPositionOfMotor(self.arm_center, self.arm_center_position)

    def moveArmForwards(self):
        if self.arm_full_position - self.ARM_FULL_STEP_EXTENDING > self.ARM_FULL_EXTENDED:
            self.arm_full_position -= self.ARM_FULL_STEP_EXTENDING
        else:
            self.arm_full_position = self.ARM_FULL_EXTENDED
        if self.arm_center_position - self.ARM_CENTER_STEP_EXTENDING > self.ARM_CENTER_EXTENDED:
            self.arm_center_position -= self.ARM_CENTER_STEP_EXTENDING
        else:
            self.arm_center_position = self.ARM_CENTER_EXTENDED
        self.setPositionOfMotor(self.arm_full, self.arm_full_position)
        self.setPositionOfMotor(self.arm_center, self.arm_center_position)

    def moveArmBackwards(self):
        if self.arm_full_position + self.ARM_FULL_STEP_RETRACTING < self.ARM_FULL_RETRACTED:
            self.arm_full_position += self.ARM_FULL_STEP_RETRACTING
        else:
            self.arm_full_position = self.ARM_FULL_RETRACTED
        if self.arm_center_position + self.ARM_CENTER_STEP_RETRACTING < self.ARM_CENTER_RETRACTED:
            self.arm_center_position += self.ARM_CENTER_STEP_RETRACTING
        else:
            self.arm_full_position = self.ARM_FULL_RETRACTED
        self.setPositionOfMotor(self.arm_full, self.arm_full_position)
        self.setPositionOfMotor(self.arm_center, self.arm_center_position)
    
    def getMinPositionOfMotor(self, motor):
        return motor.getMinPosition() if motor.getMinPosition() is not 0 else 'inf'
    
    def getMaxPositionOfMotor(self, motor):
        return motor.getMaxPosition() if motor.getMaxPosition() is not 0 else 'inf'
    
    def setPositionOfMotor(self, motor, position):
        if motor is self.arm_full:
            self.arm_full_position = position
        elif motor is self.arm_center:
            self.arm_center_position = position
        if self.getMaxPositionOfMotor(motor) is not 'inf':
            if position > self.getMaxPositionOfMotor(motor) or position < self.getMinPositionOfMotor(motor):
                return
        motor.setPosition(position)
    
    def setVelocity(self, velocity):
        if velocity > self.arm_full.getMaxVelocity() or velocity > self.arm_center.getMaxVelocity():
            return
        for motor in self.motors:
            motor.setVelocity(velocity)
        self.velocity = velocity
    
    def getMaxVelocity(self):
        return self.arm_full.getMaxVelocity() if self.arm_full.getMaxVelocity() < self.arm_center.getMaxVelocity() else self.arm_center.getMaxVelocity()

    def getVelocity(self, velocity):
        return self.velocity

class Grabber:
    grabber_full_position = 0
    grabber_back_position = 0
    grabber_front_position = 0

    velocity = 3

    GRABBER_BACK_OPENED = 0
    GRABBER_FRONT_OPENED = 0

    GRABBER_BACK_CLOSED = 1.35
    GRABBER_FRONT_CLOSED = -1.35

    GRABBER_FULL_RETRACTED_POS = 3.5
    GRABBER_BACK_RETRACTED_POS = GRABBER_BACK_CLOSED
    GRABBER_FRONT_RETRACTED_POS = GRABBER_FRONT_CLOSED


    GRABBER_FULL_IDLE_POS = 1.25
    GRABBER_BACK_IDLE_POS = GRABBER_BACK_CLOSED
    GRABBER_FRONT_IDLE_POS = GRABBER_FRONT_CLOSED

    GRABBER_FULL_WEIGH_POS = -2
    GRABBER_BACK_WEIGH_POS = GRABBER_BACK_CLOSED
    GRABBER_FRONT_WEIGH_POS = GRABBER_FRONT_CLOSED

    GRABBER_OPEN_CLOSE_STEP = 0.05

    def __init__(self, grabber_full, grabber_back, grabber_front):
        self.grabber_full = grabber_full
        self.grabber_back = grabber_back
        self.grabber_front = grabber_front
        self.motors = [self.grabber_full, self.grabber_back, self.grabber_front]
        self.setVelocity(self.velocity)
    
    def idle(self):
        self.setPositionOfMotor(self.grabber_full, self.GRABBER_FULL_IDLE_POS)
        self.setPositionOfMotor(self.grabber_back, self.GRABBER_BACK_IDLE_POS)
        self.setPositionOfMotor(self.grabber_front, self.GRABBER_FRONT_IDLE_POS)
    
    def open(self):
        self.setPositionOfMotor(self.grabber_back, self.GRABBER_BACK_OPENED)
        self.setPositionOfMotor(self.grabber_front, self.GRABBER_FRONT_OPENED)

    def close(self):
        self.setPositionOfMotor(self.grabber_back, self.GRABBER_BACK_CLOSED)
        self.setPositionOfMotor(self.grabber_front, self.GRABBER_FRONT_CLOSED)
    
    def retract(self):
        self.setPositionOfMotor(self.grabber_full, self.GRABBER_FULL_RETRACTED_POS)
        self.setPositionOfMotor(self.grabber_back, self.GRABBER_BACK_RETRACTED_POS)
        self.setPositionOfMotor(self.grabber_front, self.GRABBER_FRONT_RETRACTED_POS)
    
    def continuousOpen(self):
        if self.grabber_back_position - self.GRABBER_OPEN_CLOSE_STEP > self.GRABBER_BACK_OPENED:
            self.grabber_back_position -= self.GRABBER_OPEN_CLOSE_STEP
        else:
            self.grabber_back_position = self.GRABBER_BACK_OPENED
        if self.grabber_front_position - self.GRABBER_OPEN_CLOSE_STEP > self.GRABBER_FRONT_OPENED:
            self.grabber_front_position -= self.GRABBER_OPEN_CLOSE_STEP
        else:
            self.grabber_front_position = self.GRABBER_FRONT_OPENED
        self.setPositionOfMotor(self.grabber_back, self.grabber_back_position)
        self.setPositionOfMotor(self.grabber_front, self.grabber_front_position)
    
    def continuousClose(self):
        if self.grabber_back_position + self.GRABBER_OPEN_CLOSE_STEP < self.GRABBER_BACK_CLOSED:
            self.grabber_back_position += self.GRABBER_OPEN_CLOSE_STEP
        else:
            self.grabber_back_position = self.GRABBER_BACK_CLOSED
        if self.grabber_front_position + self.GRABBER_OPEN_CLOSE_STEP < self.GRABBER_FRONT_CLOSED:
            self.grabber_front_position += self.GRABBER_OPEN_CLOSE_STEP
        else:
            self.grabber_front_position = self.GRABBER_FRONT_CLOSED
        self.setPositionOfMotor(self.grabber_back, self.grabber_back_position)
        self.setPositionOfMotor(self.grabber_front, self.grabber_front_position)

    def goToWeighPos(self):
        self.grabber_full_position = self.GRABBER_FULL_WEIGH_POS
        self.grabber_back_position = self.GRABBER_BACK_WEIGH_POS
        self.grabber_front_position = self.GRABBER_FRONT_WEIGH_POS
        self.setPositionOfMotor(self.grabber_full, self.grabber_full_position)
        self.setPositionOfMotor(self.grabber_back, self.grabber_back_position)
        self.setPositionOfMotor(self.grabber_front, self.grabber_front_position)


    def getMinPositionOfMotor(self, motor):
        return motor.getMinPosition() if motor.getMinPosition() != 0.0 else 'inf'
    
    def getMaxPositionOfMotor(self, motor):
        return motor.getMaxPosition() if motor.getMaxPosition() != 0.0 else 'inf'

    def setPositionOfMotor(self, motor, position):
        if motor is self.grabber_full:
            self.grabber_full_position = position
        elif motor is self.grabber_back:
            self.grabber_back_position = position
        elif motor is self.grabber_front:
            self.grabber_front_position = position
        if self.getMaxPositionOfMotor(motor) is not 'inf':
            if position > self.getMaxPositionOfMotor(motor) or position < self.getMinPositionOfMotor(motor):
                return
        motor.setPosition(position)
    
    def setVelocity(self, velocity):
        if velocity > self.grabber_full.getMaxVelocity() or velocity > self.grabber_back.getMaxVelocity() or velocity > self.grabber_front.getMaxVelocity():
            return
        for motor in self.motors:
            motor.setVelocity(velocity)
        self.velocity = velocity
    
    def getMaxVelocity(self):
        return min([self.grabber_full.getMaxVelocity(), self.grabber_back.getMaxVelocity(), self.grabber_front.getMaxVelocity()])

    def getVelocity(self, velocity):
        return self.velocity

class GrabArmMotors:
    WEIGHING_TIMOUT = 128
    weighing_count = 0

    def __init__(self, Arm_Full, Arm_Center, Grabber_Full, Grabber_Back, Grabber_Front):
        self.arm = Arm(Arm_Full, Arm_Center)
        self.grabber = Grabber(Grabber_Full, Grabber_Back, Grabber_Front)
    
    def idle(self):
        self.arm.idle()
        self.grabber.idle()

    def retract(self):
        self.arm.retract()
        self.grabber.retract()

    def extendArm_Grab(self):
        self.arm.extend_Grab()
    
    def extendArm_Deposit(self):
        self.arm.extend_Deposit()
    
    def retractArm(self):
        self.arm.retract()
    
    def openGrabber(self):
        self.grabber.open()

    def closeGrabber(self):
        self.grabber.close()
    
    def setArmVelocity(self, velocity):
        self.arm.setVelocity(velocity)
    
    def setGrabberVelocity(self, velocity):
        self.grabber.setVelocity(velocity)
    
    def goToWeighPos(self):
        self.arm.goToWeighPos()
        self.grabber.goToWeighPos()

class WeighMeasurer:
    WEIGHT_OFFSET = 0.70

    def __init__(self, weight_measurer):
        self.weight_measurer = weight_measurer
    
    def getValue(self):
        return (self.weight_measurer.getValue() - self.WEIGHT_OFFSET) if (self.weight_measurer.getValue() - self.WEIGHT_OFFSET) > 0 else 0
    

class RobotControls:
    def __init__(self, Robot, timestep):
        CAMERA = 'camera'
        WHEEL = 'wheel_{}'
        GRAB_ARM = 'arm_servo_{}'
        WEIGHTSENSOR = 'weight_measure'

        self.Robot = Robot
        self.Camera = self.Robot.getCamera(CAMERA)
        self.Camera.enable(timestep)

        self.LeftWheelMotors = WheelMotors([self.Robot.getMotor(WHEEL.format(i)) for i in range(1,4)])
        self.RightWheelMotors = WheelMotors([self.Robot.getMotor(WHEEL.format(i)) for i in range(4,7)])

        arm_full, arm_center, grabber_full, grabber_back, grabber_front = tuple([self.Robot.getMotor(GRAB_ARM.format(i)) for i in range(1,6)])
        self.GrabArmMotors = GrabArmMotors(arm_full, arm_center, grabber_full, grabber_back, grabber_front)

        self.Robot.getTouchSensor(WEIGHTSENSOR).enable(timestep)
        self.WeightMeasurer = WeighMeasurer(self.Robot.getTouchSensor(WEIGHTSENSOR))

        self.MAX_WHEEL_VELOCITY = self.LeftWheelMotors.getMaxVelocity() if self.LeftWheelMotors.getMaxVelocity() < self.RightWheelMotors.getMaxVelocity() else self.RightWheelMotors.getMaxVelocity()
        self.wheel_motor_velocity = int(self.MAX_WHEEL_VELOCITY/2)

        self.MAX_ARM_VELOCITY = self.GrabArmMotors.arm.getMaxVelocity()
        self.arm_motor_velocity = int(self.MAX_ARM_VELOCITY/2)

        self.MAX_GRABBER_VELOCITY = self.GrabArmMotors.grabber.getMaxVelocity()
        self.grabber_motor_velocity = int(self.MAX_GRABBER_VELOCITY/2)

        self.GrabArmMotors.idle()
    
    def idle(self):
        self.GrabArmMotors.idle()
    
    def resetWheelVelocity(self):
        self.LeftWheelMotors.setVelocity(0)
        self.RightWheelMotors.setVelocity(0)
    
    def setWheelMotorVelocity(self, velocity):
        if velocity > self.LeftWheelMotors.getMaxVelocity() or velocity > self.RightWheelMotors.getMaxVelocity():
            return
        self.wheel_motor_velocity = velocity

    """
        velocity:
            positive: Forwards
            negative: Backwards
    """
    def goStraight(self, velocity):
        self.LeftWheelMotors.setVelocity(velocity)
        self.RightWheelMotors.setVelocity(velocity*-1)
    
    """
        velocity:
            positive: Right
            negative: Left
    """
    def turnOnSpot(self, velocity):
        self.LeftWheelMotors.setVelocity(velocity)
        self.RightWheelMotors.setVelocity(velocity)

    def strafeLeft(self, velocity):
        self.LeftWheelMotors.setVelocity(0)
        self.RightWheelMotors.setVelocity(velocity*-1)
    
    def strafeRight(self, velocity):
        self.LeftWheelMotors.setVelocity(velocity)
        self.RightWheelMotors.setVelocity(0)

    def setArmMotorVelocity(self, velocity):
        if velocity > self.GrabArmMotors.arm.getMaxVelocity():
            return
        self.arm_motor_velocity = velocity
    
    def setGrabberMotorVelocity(self, velocity):
        if velocity > self.GrabArmMotors.grabber.getMaxVelocity():
            return
        self.grabber_motor_velocity = velocity

    def extendArm(self, distance, velocity):
        if distance is 'inf':
            self.GrabArmMotors.extendArm()
        self.GrabArmMotors.arm.moveArm(distance)
        self.GrabArmMotors.arm.setVelocity(velocity)
        

    def retractArm(self, distance, velocity):
        if distance is 'inf':
            self.GrabArmMotors.retractArm()
        self.GrabArmMotors.arm.moveArm(distance*-1)
        self.GrabArmMotors.arm.setVelocity(velocity)
    
    def openGrabber(self, distance, velocity):
        if distance is 'inf':
            pass
    
    def closeGrabber(self, distance, velocity):
        if distance is 'inf':
            pass