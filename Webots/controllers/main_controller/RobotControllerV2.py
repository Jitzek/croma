from KeyCodes import KeyCodes as kc
import TaskCodes
from TaskCodes import TaskCodes as tc
import ActionCodes
from ActionCodes import ActionCodes as ac
from functools import partial
import math
import Constants
import websocket
import _thread
import json
from pprint import pprint

from tasks.tasks import Tasks
from actions.actions import Actions

class RobotController:
    is_manual = True

    current_task = tc.NONE
    current_action = ac.NONE
    current_command = 'NONE'
    previous_command = 'NONE'
    additional_command = 'NONE'

    def __init__(self, rbc, url, socket, vision_display = False):
        self.rbc = rbc
        self.vision_display = vision_display
        self.socket = socket
        if self.socket:
            self._socket_connect()
        self.tasks = Tasks(self.rbc, self.socket, self.vision_display)
        self.actions = Actions(self.rbc)
        
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(url,
            on_message = lambda ws, msg: self.on_command(ws, msg),
            on_open = lambda ws: self.on_open(ws),
            on_error = lambda ws, msg: self.on_error(ws, msg),
            on_close = lambda ws: self.on_close(ws))
        _thread.start_new_thread(self.ws.run_forever,())
    
    
    def on_command(self, ws, message):
        self.current_command = json.loads(message)['command']
        
    def on_open(self, ws):
        print("### Connected ###")
        
    def on_error(self, ws, msg):
        print("an error has occured")
        
    def on_close(self, ws):
        print("closing...")
    """
        Main Update Logic for the Robot
    """
    def Update(self):
        # Refresh vision_display if defined
        if self.vision_display:
            self.vision_display.refresh(self.rbc.Camera.getImageArray())
        
        # Auto reconnect socket if connection has been lost
        self._socket_connect()
        
        self._handle_command()
        self._handle_additional_commands()
        self.previous_command = self.current_command

        # Action has priority over Task
        if self.hasAction():
            if self.actions.execAction(self.current_action):
                self.switchAction(ac.NONE)
                self.actions.resetAllActions()
        elif self.hasTask():
            if self.tasks.execTask(self.current_task, self.additional_command):
                self.switchTask(tc.NONE)
                self.tasks.resetAllActions()

    def hasTask(self):
        return self.current_task is not tc.NONE
    
    def hasAction(self):
        return self.current_action is not ac.NONE

    def switchTask(self, task):
        if self.current_task is task:
            return
        if task not in [t for t in tc]:
            return
        if task == tc.NONE:
            self.tasks.forceStop()
            self.rbc.idle()
        self.tasks.resetAllActions()
        self.current_task = task
        self.disableManual()

        self._socket_send(Constants.JSON_PREFIX.format('{', TaskCodes.translateTaskToString(self.current_task), '', '', '', '}'))
        print('Changed Current Task to: "{}"'.format(TaskCodes.translateTaskToString(self.current_task)))
    
    def _handle_additional_commands(self):
        if self.current_command in ["HEARTS", "CLUBS", "DIAMONDS", "SPADES"]:
            self.additional_command = self.current_command
            return
        self.additional_command = "NONE"
        
    def switchAction(self, action):
        if self.current_action is action:
             return
        if action not in [t for t in ac]:
            return
        if action == ac.NONE:
            self.actions.forceStop()
            self.rbc.idle()
        self.actions.resetAllActions()
        self.current_action = action
        self.disableManual()

        print('Changed Current Action to: "{}"'.format(ActionCodes.translateActionToString(self.current_action)))

    def toggleManual(self):
        if self.is_manual is True:
            self.disableManual()
            return
        self.enableManual()

    def enableManual(self):
        if self.is_manual:
            return
        #if self.current_task is not tc.NONE:
        #    self.switchTask(tc.NONE)
        self.is_manual = True
        print('Manual Controls Enabled')

    def disableManual(self):
        if not self.is_manual:
            return
        self.is_manual = False
        print('Manual Controls Disabled')
    
    def _socket_send(self, json_string):
        if not self.socket or not self.socket.isConnected():
            return
        self.socket.send(json_string)
    
    def _socket_connect(self):
        if not self.socket or self.socket.isConnected():
            return
        self.socket.connect()

    # Default method for switch case, leave empty
    def _Default(self):
        pass

    def _handle_command(self):
        self.rbc.resetWheelVelocity()
        
        self._handle_continuous_command()
        self._handle_speed_change()
        
        #if prev != current then toggle else don't toggle
        if(self.previous_command != self.current_command):
            self._handle_toggle_command()
        

    def _handle_continuous_command(self):
        {
            'GO_FORWARDS': partial(self.rbc.goStraight, self.rbc.wheel_motor_velocity),
            'TURN_ON_SPOT_LEFT': partial(self.rbc.turnOnSpot, self.rbc.wheel_motor_velocity  * -1),
            'GO_BACKWARDS': partial(self.rbc.goStraight, self.rbc.wheel_motor_velocity * -1),
            'TURN_ON_SPOT_RIGHT': partial(self.rbc.turnOnSpot, self.rbc.wheel_motor_velocity),
            'FORWARD_TURN_LEFT': partial(self.rbc.turnLeft, self.rbc.wheel_motor_velocity),
            'FORWARD_TURN_RIGHT': partial(self.rbc.turnRight, self.rbc.wheel_motor_velocity),
            'BACKWARD_TURN_RIGHT': partial(self.rbc.turnLeft, self.rbc.wheel_motor_velocity * -1),
            'BACKWARD_TURN_LEFT': partial(self.rbc.turnRight, self.rbc.wheel_motor_velocity  * -1),
        }.get(self.current_command, lambda: self.default)()
    
    def _handle_toggle_command(self):
        {
            'CLEAR_ACTION': partial(self.switchAction, ac.NONE),
            'TOGGLE_ACTION_GRABARM_GRAB_OBJECT': partial(self.switchAction, ac.GRAB_OBJECT),
            'TOGGLE_ACTION_GRABARM_WEIGH_OBJECT': partial(self.switchAction, ac.WEIGH_OBJECT),
            'TOGGLE_ACTION_GRABARM_DEPOSIT_OBJECT': partial(self.switchAction, ac.DEPOSIT_OBJECT),
            'TOGGLE_ACTION_COLLECT_MINERAL': partial(self.switchAction, ac.COLLECT_MINERAL),
            'RETRACT_GRABARM': partial(self.rbc.GrabArmMotors.retract),
            'RESET_ARM': partial(self.rbc.GrabArmMotors.idle),
            'TOGGLE_MANUAL': partial(self.toggleManual),
            'CLEAR_TASK': partial(self.switchTask, tc.NONE),
            'TOGGLE_TASK_SCAN_QR_CODE': partial(self.switchTask, tc.SCAN_QR_CODE),
            'TOGGLE_TASK_FIND_CARD_SYMBOL': partial(self.switchTask, tc.FIND_CARD_SYMBOL),
            'TOGGLE_TASK_RECOGNIZE_TEMPERATURE': partial(self.switchTask, tc.MEASURE_TEMP_OF_WATER_SOURCE),
            'TOGGLE_TASK_DANCING_ON_THE_MOON': partial(self.switchTask, tc.DANCING_ON_THE_MOON),
            'TOGGLE_TASK_MOON_MAZE': partial(self.switchTask, tc.MOON_MAZE),
            'TOGGLE_TASK_MINERAL_ANALYSIS': partial(self.switchTask, tc.MINERAL_ANALYSIS),
            'TOGGLE_TASK_MOON_WALK': partial(self.switchTask, tc.MOON_WALK),
            'TOGGLE_TASK_MOON_SURVIVAL': partial(self.switchTask, tc.MOON_SURVIVAL),
        }.get(self.current_command, lambda: self.default)()
    
    def _handle_speed_change(self):
        for i in range (1, 11):
            if 'SPEED_{}'.format(i) == self.current_command:
                self.rbc.setWheelMotorVelocity((self.rbc.MAX_WHEEL_VELOCITY / 10) * i)
                break
    def default(self):
        return