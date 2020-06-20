from actions.grab_object import GrabObject
from actions.weigh_object import WeighObject
from actions.deposit_object import DepositObject
from actions.collect_mineral import CollectMineral
from actions.search_and_deposit_into_tray import SearchAndDepositIntoTray
from ActionCodes import ActionCodes as ac
import ActionCodes

class Actions:
    force_stop = False

    def __init__(self, rbc):
        self.rbc = rbc
        self.ACTIONS = {
            ac.GRAB_OBJECT: GrabObject(self.rbc),
            ac.WEIGH_OBJECT: WeighObject(self.rbc),
            ac.DEPOSIT_OBJECT: DepositObject(self.rbc),
            ac.COLLECT_MINERAL: CollectMineral(self.rbc)
        }
    
    def forceStop(self):
        self.force_stop = True

    def execAction(self, action_code):
        if self.force_stop:
            self.force_stop = False
            return False
        return self.ACTIONS.get(action_code, self._Default).execute()
    
    def resetAllActions(self):
        self.force_stop = False
        for key in self.ACTIONS:
            self.ACTIONS[key].reset()

    def _Default(self):
        return True
    
