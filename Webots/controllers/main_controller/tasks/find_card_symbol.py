from vision.card_symbol_recognition import CardSymbolRecognition, Symbols, symbolToString
import Constants


from enum import Enum, auto, unique
@unique
class Stage(Enum):
    NONE = auto()
    WAIT_FOR_INPUT = auto()
    FIND_SYMBOL = auto()
    GO_TO_SYMBOL = auto()

class FindCardSymbol:
    prev_stage = Stage.NONE
    current_stage = Stage.WAIT_FOR_INPUT
    symbol = False

    def __init__(self, rbc, socket=False, vision_display=False):
        self.rbc = rbc
        self.csr = CardSymbolRecognition(self.rbc.Camera)
        self.socket = socket
        self.vision_display = vision_display

    def _stage_to_string(self, stage, symbol = 'undefined'):
        return {
            Stage.NONE: 'NaN',
            Stage.WAIT_FOR_INPUT: 'Waiting for input',
            Stage.FIND_SYMBOL: 'Looking for {} symbol'.format(symbol.upper()),
            Stage.GO_TO_SYMBOL: 'Going to {} symbol'.format(symbol.upper())
        }.get(stage, 'NaN')
    
    def _socket_send_current_stage(self):
        if self.socket:
            if self.prev_stage != self.current_stage:
                self.socket.send(Constants.JSON_PREFIX.format('{', 'Finding Card Symbol', self._stage_to_string(self.current_stage, symbolToString(self.symbol)), '', '', '}'))
                self.prev_stage = self.current_stage
    
    def reset(self):
        self.current_stage = Stage.WAIT_FOR_INPUT
        self.prev_stage = Stage.NONE
        self.symbol = False
        self.csr = CardSymbolRecognition(self.rbc.Camera)

    def execute(self):
        self._socket_send_current_stage()

        if self.current_stage == Stage.WAIT_FOR_INPUT:
            if ord('K') in self.rbc.keys:
                self.symbol = Symbols.KLAVER
            if ord('S') in self.rbc.keys:
                self.symbol = Symbols.SCHOPPEN
            if ord('H') in self.rbc.keys:
                self.symbol = Symbols.HARTEN
            if ord('R') in self.rbc.keys:
                self.symbol = Symbols.RUITEN
            if self.symbol:
                self.current_stage = Stage.FIND_SYMBOL
                if self.socket:
                    self.socket.send(Constants.JSON_PREFIX.format('{', 'Finding Card Symbol', self._stage_to_string(self.current_stage, symbolToString(self.symbol)), 'Card Symbol', symbolToString(self.symbol), '}'))
            return False
        
        if self.current_stage == Stage.FIND_SYMBOL:
            center_x = self.csr.get_pos_match(self.symbol)
            if center_x:
                self._goToPosition(center_x)
                self.current_stage = Stage.GO_TO_SYMBOL
                return False
            self._spin()
            return False
        
        if self.current_stage == Stage.GO_TO_SYMBOL:
            center_x = self.csr.get_pos_match(self.symbol)
            if center_x:
                self._goToPosition(center_x)
            return False

        return True

    def _spin(self):
        self.rbc.turnOnSpot(3)
    
    def _goToPosition(self, x):
        camera_width = self.rbc.Camera.getWidth()
        X_DEV = (camera_width/2)/10
        min_x = camera_width/2 - X_DEV
        max_x = camera_width/2 + X_DEV
        if min_x <= x <= max_x:
            self.rbc.goStraight(2)
        elif x > max_x:
            self.rbc.turnOnSpot(2)
        elif x < min_x:
            self.rbc.turnOnSpot(-2)