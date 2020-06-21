import Constants
from audio.audio import get_beat_times
class MoonWalk:
    beat_times = []
    FILE_PATH = "audio/linedance.mp3"
    index = 0
    time_step = (Constants.TIMESTEP / 2) / 1000
    current_time = 0
    head_forwards = False
    
    def __init__(self, rbc, socket=False, vision_display=False):
        self.rbc = rbc
        print(get_beat_times(self.FILE_PATH))
    
    def reset(self):
        self.index = 0
        self.beat_times = []
        self.head_forwards = False
        self.current_time = 0

    def execute(self, command = False):
        self.current_time += self.time_step
        if len(self.beat_times) == 0:
            self.beat_times = get_beat_times(self.FILE_PATH)
            return False
        if self.index >= len(self.beat_times):
            return True
        if self.current_time < self.beat_times[self.index]:
            return False
        self.index += 1
        #beat detected
        self._bop_head()
        self.head_bob = True
        return False
    
    def _bop_head(self):
        
        self.rbc.setGrabberMotorVelocity(self.rbc.GrabArmMotors.grabber.getMaxVelocity())
        self.rbc.setArmMotorVelocity(self.rbc.GrabArmMotors.arm.getMaxVelocity())
        if self.head_forwards:
            self.rbc.GrabArmMotors.grabber.setPositionOfMotor(self.rbc.GrabArmMotors.grabber.grabber_full, 1.3)
            self.head_forwards = False
            return
        self.rbc.GrabArmMotors.grabber.setPositionOfMotor(self.rbc.GrabArmMotors.grabber.grabber_full, 1.0)
        self.head_forwards = True

