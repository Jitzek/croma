from enum import Enum, auto, unique

@unique
class ActionCodes(Enum):
    NONE = auto()
    GRAB_OBJECT = auto()
    WEIGH_OBJECT = auto()
    DEPOSIT_OBJECT = auto()
    COLLECT_MINERAL = auto()

def translateActionToString(action):
    return {
        ActionCodes.NONE: 'Idling',
        ActionCodes.GRAB_OBJECT: 'Grabbing Object',
        ActionCodes.WEIGH_OBJECT: 'Weighing Object',
        ActionCodes.DEPOSIT_OBJECT: 'Depositing Object',
        ActionCodes.COLLECT_MINERAL: 'Collecting Mineral'
    }.get(action, 'Invalid Action')