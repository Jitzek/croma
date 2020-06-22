class DriveToCup:

    def __init__(self, robot):
        self.robot = robot
        self.leftFrontMotor = robot.getMotor('wheel_6')
        self.leftMidMotor = robot.getMotor('wheel_5')
        self.leftRearMotor = robot.getMotor('wheel_4')

        self.rightFrontMotor = robot.getMotor('wheel_3')
        self.rightMidMotor = robot.getMotor('wheel_2')
        self.rightRearMotor = robot.getMotor('wheel_1')

    def steerTo(self, x, width):
        X_DEV = (width / 2) / 10
        min_x = width / 2 - X_DEV
        max_x = width / 2 + X_DEV
        if min_x <= x <= max_x:
            self.setPositions()
            self.forward(2)
        elif x > max_x:
            self.setPositions()
            self.turn(2)
        elif x < min_x:
            self.setPositions()
            self.turn(-2)

    def setPositions(self):
        self.leftFrontMotor.setPosition(float('inf'))
        self.leftMidMotor.setPosition(float('inf'))
        self.leftRearMotor.setPosition(float('inf'))

        self.rightFrontMotor.setPosition(float('inf'))
        self.rightMidMotor.setPosition(float('inf'))
        self.rightRearMotor.setPosition(float('inf'))

    def forward(self, x):
        self.leftFrontMotor.setVelocity(-x)
        self.leftMidMotor.setVelocity(-x)
        self.leftRearMotor.setVelocity(-x)
        self.rightFrontMotor.setVelocity(x)
        self.rightMidMotor.setVelocity(x)
        self.rightRearMotor.setVelocity(x)

    def turn(self, x):
        self.leftFrontMotor.setVelocity(x)
        self.leftMidMotor.setVelocity(x)
        self.leftRearMotor.setVelocity(x)
        self.rightFrontMotor.setVelocity(x)
        self.rightMidMotor.setVelocity(x)
        self.rightRearMotor.setVelocity(x)

    def brake(self):
        self.leftFrontMotor.setVelocity(0.0)
        self.leftMidMotor.setVelocity(0.0)
        self.leftRearMotor.setVelocity(0.0)
        self.rightFrontMotor.setVelocity(0.0)
        self.rightMidMotor.setVelocity(0.0)
        self.rightRearMotor.setVelocity(0.0)

    def reverse(self, x):
        self.leftFrontMotor.setVelocity(x)
        self.leftMidMotor.setVelocity(x)
        self.leftRearMotor.setVelocity(x)
        self.rightFrontMotor.setVelocity(-x)
        self.rightMidMotor.setVelocity(-x)
        self.rightRearMotor.setVelocity(-x)