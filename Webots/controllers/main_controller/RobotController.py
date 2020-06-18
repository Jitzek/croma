from KeyCodes import KeyCodes as kc
import TaskCodes
from TaskCodes import TaskCodes as tc
import ActionCodes
from ActionCodes import ActionCodes as ac
from functools import partial
import math
import Constants

from tasks.tasks import Tasks
from actions.actions import Actions

class RobotController:
    CURLY_BRACKET_OPEN = '{'
    CURLY_BRACKET_CLOSE = '}'

    # Prevents toggled actions from taking place multiple times in one key press
    TOGGLE_TIMEOUT = 42
    toggle_timeout_count = TOGGLE_TIMEOUT

    manual_wheel_velocity = 5
    is_manual = True

    current_task = tc.NONE
    current_action = ac.NONE

    def __init__(self, rbc, kb, vision_display = False, socket = False):
        self.rbc = rbc
        self.kb = kb
        self.vision_display = vision_display
        self.socket = socket
        if self.socket:
            self._socket_connect()
        self.tasks = Tasks(self.rbc, self.socket, self.vision_display)
        self.actions = Actions(self.rbc)
    
    """
        Main Update Logic for the Robot
    """
    def Update(self):
        if self.vision_display:
            self.vision_display.refresh(self.rbc.Camera.getImageArray())
        
        # Auto reconnect socket if connection has been lost
        self._socket_connect()
        
        # Handle User Input
        self._handleUserInput()

        # Action has priority over Task
        if self.hasAction():
            if self.actions.execAction(self.current_action):
                self.switchAction(ac.NONE)
                self.actions.resetAllActions()
        elif self.hasTask():
            if self.tasks.execTask(self.current_task):
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

        self._socket_send(Constants.JSON_PREFIX.format(self.CURLY_BRACKET_OPEN, TaskCodes.translateTaskToString(self.current_task), '', '', '', self.CURLY_BRACKET_CLOSE))
        print('Changed Current Task to: "{}"'.format(TaskCodes.translateTaskToString(self.current_task)))
    
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

        ### TODO: Send to Website through Socket (as JSON) ###
        print('Changed Current Action to: "{}"'.format(ActionCodes.translateActionToString(self.current_action)))

    def toggleManual(self):
        if self.is_manual is True:
            self.disableManual()
            return
        self.enableManual()

    def enableManual(self):
        if self.is_manual:
            return
        if self.current_task is not tc.NONE:
            self.switchTask(tc.NONE)
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

    def _handleUserInput(self):
        self.rbc.keys = self._getActiveKeys()

        # Reset robot movement
        self.rbc.resetWheelVelocity()

        if self._handleToggledInput(self.rbc.keys):
            self.toggle_timeout_count = 0
            return

        self._handleContinuousInput(self.rbc.keys)
    
    def _getActiveKeys(self):
        # Get list of all pressed keys
        keys = []
        while True:
            key = self.kb.getKey()
            if key is -1: break
            keys.append(key)
        return keys
    
    def _handleToggledInput(self, keys):
        if self.toggle_timeout_count < self.TOGGLE_TIMEOUT:
            self.toggle_timeout_count += 1
            return False
        
        # Handle Single Input Event (return if handled)
        if self._handleSingleInput(keys):
            return True

        # Handle Dual Input Event (return if handled)
        if self._handleDualInput(keys):
            return True
        
        return False

    def _handleContinuousInput(self, keys):
        # Handle manual movement
        self._handleManualMovement(keys)
        
    def _handleManualMovement(self, keys):
        """
            Manual Movement (needs to be enabled)
        """
        if self.is_manual:
            # Set manual velocity wheels
            self._handleManualWheelSpeedChange(keys)

            # Set manual velocity grabarm
            self._handleManualArmSpeedChange(keys)
            self._handleManualGrabberSpeedChange(keys)

            # Handle manual wheel movement
            self._handleManualWheelsMovement(keys)

            # Handle manual grabarm movement
            self._handleManualGrabArmMovement(keys)

    def _handleManualWheelSpeedChange(self, keys):
        movement = False
        option = False
        for key in keys:
            if key in kc.WHEEL_MOVEMENT_KEYS:
                movement = key
            if key in kc.SPEED_OPTIONS:
                velocity_step = math.floor(self.rbc.MAX_WHEEL_VELOCITY/10)
                option = int(chr(key) * velocity_step) if key != ord('0') else int(10 * velocity_step)
            if not movement or not option:
                continue
            self.rbc.setWheelMotorVelocity(option)
            break
    
    def _handleManualArmSpeedChange(self, keys):
        movement = False
        option = False
        for key in keys:
            if key in kc.ARM_MOVEMENT_KEYS:
                movement = key
            if key in kc.SPEED_OPTIONS:
                velocity_step = math.floor(self.rbc.MAX_ARM_VELOCITY/10)
                option = int(chr(key) * velocity_step) if key != ord('0') else int(10 * velocity_step)
            if not movement or not option:
                continue
            self.rbc.GrabArmMotors.arm.setVelocity(option)
            break
        
    def _handleManualGrabberSpeedChange(self, keys):
        movement = False
        option = False
        for key in keys:
            if key in kc.GRABBER_MOVEMENT_KEYS:
                movement = key
            if key in kc.SPEED_OPTIONS:
                velocity_step = math.floor(self.rbc.MAX_GRABBER_VELOCITY/10)
                option = int(chr(key) * velocity_step) if key != ord('0') else int(10 * velocity_step)
            if not movement or not option:
                continue
            self.rbc.GrabArmMotors.grabber.setVelocity(option)
            break
    
    def _handleSingleInput(self, keys):
        # Return if not only one input
        if len(keys) is not 1:
            return False
        
        key = keys[0]

        # Toggle Manual
        if kc.TOGGLE_MANUAL_KEY == key:
            self.toggleManual()
            return True
        
        # Retract Arm
        if kc.GRABARM_RETRACT_KEY == key:
            self.rbc.GrabArmMotors.retract()
            return True

        if kc.RESET_ARM_KEY == key:
            self.rbc.GrabArmMotors.idle()
            return True

        if key in kc.TOGGLE_ACTION_KEYS:
            {
                kc.CLEAR_ACTION: partial(self.switchAction, ac.NONE),
                kc.TOGGLE_ACTION_GRABARM_GRAB_OBJECT_KEY: partial(self.switchAction, ac.GRAB_OBJECT),
                kc.TOGGLE_ACTION_GRABARM_WEIGH_OBJECT_KEY: partial(self.switchAction, ac.WEIGH_OBJECT),
                kc.TOGGLE_ACTION_GRABARM_DEPOSIT_OBJECT_KEY: partial(self.switchAction, ac.DEPOSIT_OBJECT),
                kc.TOGGLE_ACTION_COLLECT_MINERAL_KEY: partial(self.switchAction, ac.COLLECT_MINERAL)
            }.get(key, lambda: self._Default)()
            return True
        
        # Task toggles (0-9, starts with '1', ends at '0')
        # '-' clears current task
        if key in kc.TOGGLE_TASK_KEYS:
            {
                kc.CLEAR_TASK_KEY: partial(self.switchTask, tc.NONE),
                kc.TOGGLE_TASK_DANCING_ON_THE_MOON_KEY: partial(self.switchTask, tc.DANCING_ON_THE_MOON),
                kc.TOGGLE_TASK_MOON_MAZE_KEY: partial(self.switchTask, tc.MOON_MAZE),
                kc.TOGGLE_TASK_MOON_SURVIVAL_KEY: partial(self.switchTask, tc.MOON_SURVIVIVAL),
                kc.TOGGLE_TASK_FIND_CARD_SYMBOL_KEY: partial(self.switchTask, tc.FIND_CARD_SYMBOL),
                kc.TOGGLE_TASK_MEASURE_TEMP_OF_WATER_SOURCE_KEY: partial(self.switchTask, tc.MEASURE_TEMP_OF_WATER_SOURCE),
                kc.TOGGLE_TASK_SCAN_QR_CODE_KEY: partial(self.switchTask, tc.SCAN_QR_CODE),
                kc.TOGGLE_TASK_MINERAL_ANALYSIS_KEY: partial(self.switchTask, tc.MINERAL_ANALYSIS)
            }.get(key, lambda: self._Default)()
            return True

        return False
    
    def _handleDualInput(self, keys):
        # Return if not only two inputs
        if len(keys) is not 2:
            return False
        
        return False
    
    def _handleManualWheelsMovement(self, keys):
        # STRAFING
        if kc.FORWARD_KEY in keys and kc.LEFT_KEY in keys:
            self.rbc.turnLeft(self.rbc.wheel_motor_velocity)
            return
        if kc.FORWARD_KEY in keys and kc.RIGHT_KEY in keys:
            self.rbc.turnRight(self.rbc.wheel_motor_velocity)
            return
        if kc.BACKWARD_KEY in keys and kc.LEFT_KEY in keys:
            self.rbc.turnRight(self.rbc.wheel_motor_velocity*-1)
            return
        if kc.BACKWARD_KEY in keys and kc.RIGHT_KEY in keys:
            self.rbc.turnLeft(self.rbc.wheel_motor_velocity*-1)
            return

        # ON POSITION
        if kc.FORWARD_KEY in keys:
            self.rbc.goStraight(self.rbc.wheel_motor_velocity)
            return
        if kc.BACKWARD_KEY in keys:
            self.rbc.goStraight(self.rbc.wheel_motor_velocity*-1)
            return
        if kc.LEFT_KEY in keys:
            self.rbc.turnOnSpot(self.rbc.wheel_motor_velocity*-1)
            return
        if kc.RIGHT_KEY in keys:
            self.rbc.turnOnSpot(self.rbc.wheel_motor_velocity)
            return
    
    def _handleManualGrabArmMovement(self, keys):
        # Arm
        if kc.ARM_EXTEND_KEY in keys:
            self.rbc.GrabArmMotors.arm.moveArmForwards()
        elif kc.ARM_RETRACT_KEY in keys:
            self.rbc.GrabArmMotors.arm.moveArmBackwards()
        
        # Grabber
        if kc.GRABBER_OPEN_KEY in keys:
            self.rbc.GrabArmMotors.grabber.continuousOpen()
        elif kc.GRABBER_CLOSE_KEY in keys:
            self.rbc.GrabArmMotors.grabber.continuousClose()


    # Default method for switch case, leave empty
    def _Default(self):
        pass
