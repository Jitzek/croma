from vision.card_symbol_recognition import CardSymbolRecognition, Symbols

from enum import Enum, auto, unique
@unique
class Stage(Enum):
    WAIT_FOR_INPUT = auto()
    FIND_SYMBOL = auto()
    GO_TO_SYMBOL = auto()

class FindCardSymbol:
    current_stage = Stage.WAIT_FOR_INPUT
    symbol = False

    def __init__(self, rbc, socket=False):
        self.rbc = rbc
        self.csr = CardSymbolRecognition(self.rbc.Camera)
        self.socket = socket
    
    def reset(self):
        self.current_stage = Stage.WAIT_FOR_INPUT
        self.symbol = False
        self.csr = CardSymbolRecognition(self.rbc.Camera)

    def execute(self):
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
            return False
        
        if self.current_stage == Stage.FIND_SYMBOL:
            center_x = self.csr.get_pos_match(self.symbol)
            if center_x:
                self._goToPosition(center_x)
                return False
            self._spin()
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