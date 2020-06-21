from enum import Enum, auto, unique

@unique
class TaskCodes(Enum):
    NONE = auto()
    SCAN_QR_CODE = auto()
    MEASURE_TEMP_OF_WATER_SOURCE = auto()
    DANCING_ON_THE_MOON = auto()
    MOON_SURVIVIVAL = auto()
    MOON_MAZE = auto()
    FIND_CARD_SYMBOL = auto()
    MINERAL_ANALYSIS = auto()
    MOON_WALK = auto()

def translateTaskToString(task):
    return {
        TaskCodes.NONE: 'No Task',
        TaskCodes.SCAN_QR_CODE: 'Scan QR Code',
        TaskCodes.MEASURE_TEMP_OF_WATER_SOURCE: 'Measuring Temperature of Water Source',
        TaskCodes.DANCING_ON_THE_MOON: 'Dancing on the Moon',
        TaskCodes.MOON_SURVIVIVAL: 'Moon Survival',
        TaskCodes.MOON_MAZE: 'Moon Maze',
        TaskCodes.FIND_CARD_SYMBOL: 'Finding Card Symbol',
        TaskCodes.MINERAL_ANALYSIS: 'Mineral Analysis',
        TaskCodes.MOON_WALK: 'Moon walk',
    }.get(task, 'Invalid Task')