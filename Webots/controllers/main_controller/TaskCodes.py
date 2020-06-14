from enum import Enum, auto, unique

@unique
class TaskCodes(Enum):
    NONE = auto()
    SCAN_QR_CODE = auto()
    RECOGNIZE_SYMBOL = auto()
    RECOGNIZE_TEMPERATURE = auto()
    DANCING_ON_THE_MOON = auto()
    MOON_SURVIVIVAL = auto()
    MOON_MAZE = auto()

def translateTaskToString(task):
    return {
        TaskCodes.NONE: 'No Task',
        TaskCodes.SCAN_QR_CODE: 'Scan QR Code',
        TaskCodes.RECOGNIZE_SYMBOL: 'Recognize Card Symbol',
        TaskCodes.RECOGNIZE_TEMPERATURE: 'Recognize Temperature',
        TaskCodes.DANCING_ON_THE_MOON: 'Dancing on the Moon',
        TaskCodes.MOON_SURVIVIVAL: 'Moon Survival',
        TaskCodes.MOON_MAZE: 'Moon Maze'
    }.get(task, 'Invalid Task')