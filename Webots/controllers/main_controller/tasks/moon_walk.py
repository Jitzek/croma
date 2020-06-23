import Constants
from audio.audio_analysing import AudioAnalysing
import numpy as np
class MoonWalk:
    beat_times = []
    FILE_PATH = "audio/linedance.mp3"
    index = 0
    time_step = (Constants.TIMESTEP/2) / 1000
    current_time = 0
    head_forwards = False
    
    def __init__(self, rbc, socket=False, vision_display=False):
        self.rbc = rbc
        self.socket = socket
    
    def reset(self):
        self.index = 0
        self.beat_times = []
        self.head_forwards = False
        self.current_time = 0

    def execute(self, command = False):
        # Get timestamps of beats if not already defined
        if len(self.beat_times) == 0:
            self.aa = AudioAnalysing(self.FILE_PATH)
            self.beat_times = self.aa.get_dynamic_beat_times()
            return False
        self.rbc.LEDMatrix.update(self._get_decibel_matrix())
        self.current_time += self.time_step
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

    #gets the decibel value of the current time of a certain frequency
    def _get_decibel(self, time, freq):
        return self.aa.specto[int(freq[0] * self.aa._get_frequencies_index_ratio(freq))][int(time * self.aa.time_index_ratio)]

    def _get_decibel_matrix(self):
        return [self._get_decibel(self.current_time, ledbar.range) for ledbar in self.rbc.LEDMatrix.LEDbars]