from vision.temperature_recognition import measureColorTemp
import Constants

class RecognizeTemperature:
    current_result = False

    def __init__(self, rbc, socket=False, vision_display=False):
        self.rbc = rbc
        self.socket = socket
        self.vision_display = vision_display
    
    def reset(self):
        pass

    def execute(self):
        self._draw_point_of_interest()
        result = measureColorTemp(self.rbc.Camera)
        if self.socket:
            if self.current_result and self.current_result != result:
                self.socket.send(Constants.JSON_PREFIX.format('{', 'Recognize Temperature', 'Temperature', result, '}'))
        self.current_result = result
        return False

    def _draw_point_of_interest(self):
        if self.vision_display:
            self.vision_display.setColor(0x09ff00)
            self.vision_display.drawRectangle(int(self.rbc.Camera.getWidth()/2), int(self.rbc.Camera.getHeight()/2), 20, 20)