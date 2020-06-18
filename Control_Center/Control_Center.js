//array with keys pressed at the same time
var keys = [];

let prev_command = "NONE";

const socket = new WebSocket("ws://localhost:3333");
const ORIGIN = "controller";

/**
 * below are constant objects containing info of all commands,
 * like the commands itself, it's keycode and the key(s) that needs to be pressed for the command
 */
const GO_FORWARDS = {
  name: "GO_FORWARDS",
  keycode: 87,
  key: 'w',
};
const TURN_ON_SPOT_LEFT = {
  name: "TURN_ON_SPOT_LEFT",
  keycode: 65,
  key: 'a',
};
const GO_BACKWARDS = {
  name: "GO_BACKWARDS",
  keycode: 83,
  key: "s",
};
const TURN_ON_SPOT_RIGHT = {
  name: "TURN_ON_SPOT_RIGHT",
  keycode: 68,
  key: "d",
};
const CLEAR_ACTION = {
  name: "CLEAR_ACTION",
  keycode: 191,
  key: "/",
};
const TOGGLE_ACTION_GRABARM_GRAB_OBJECT = {
  name: "TOGGLE_ACTION_GRABARM_GRAB_OBJECT",
  keycode: 220,
  key: "\\",
};
const TOGGLE_ACTION_GRABARM_WEIGH_OBJECT = {
  name: "TOGGLE_ACTION_GRABARM_WEIGH_OBJECT",
  keycode: 36,
  key: "HOME",
};
const TOGGLE_ACTION_GRABARM_DEPOSIT_OBJECT = {
  name: "TOGGLE_ACTION_GRABARM_DEPOSIT_OBJECT",
  keycode: 13,
  key: "ENTER",
};
const TOGGLE_ACTION_COLLECT_MINERAL = {
  name: "TOGGLE_ACTION_COLLECT_MINERAL",
  keycode: 77,
  key: "m",
};
const RETRACT_GRABARM = {
  name: "RETRACT_GRABARM",
  keycode: 61,
  key: "=",
};
const RESET_ARM = {
  name: "RESET_ARM",
  keycode: 35,
  key: "END",
};
const TOGGLE_MANUAL = {
  name: "TOGGLE_MANUAL",
  keycode: 84,
  key: "t",
};
const CLEAR_TASK = {
  name: "CLEAR_TASK",
  keycode: 173,
  key: "-",
};
const TOGGLE_TASK_SCAN_QR_CODE = {
  name: "TOGGLE_TASK_SCAN_QR_CODE",
  keycode: 49,
  key: "1",
};
const TOGGLE_TASK_FIND_CARD_SYMBOL = {
  name: "TOGGLE_TASK_FIND_CARD_SYMBOL",
  keycode: 50,
  key: "2",
};
const TOGGLE_TASK_RECOGNIZE_TEMPERATURE = {
  name: "TOGGLE_TASK_RECOGNIZE_TEMPERATURE",
  keycode: 51,
  key: "3",
};
const TOGGLE_TASK_DANCING_ON_THE_MOON = {
  name: "TOGGLE_TASK_DANCING_ON_THE_MOON",
  keycode: 52,
  key: "4",
};
const TOGGLE_TASK_MOON_SURVIVAL = {
  name: "TOGGLE_TASK_MOON_SURVIVAL",
  keycode: 53,
  key: "5",
};
const TOGGLE_TASK_MOON_MAZE = {
  name: "TOGGLE_TASK_MOON_MAZE",
  keycode: 54,
  key: "6",
};
const TOGGLE_TASK_MINERAL_ANALYSIS = {
  name: "TOGGLE_TASK_MINERAL_ANALYSIS",
  keycode: 55,
  key: "7",
};
const FORWARD_TURN_LEFT = {
  name: "FORWARD_TURN_LEFT",
  keycode: [65, 87],
  key: "a+w",
};
const FORWARD_TURN_RIGHT = {
  name: "FORWARD_TURN_RIGHT",
  keycode: [68, 87],
  key: "d+w",
};
const BACKWARD_TURN_RIGHT = {
  name: "BACKWARD_TURN_RIGHT",
  keycode: [65, 83],
  key: "a+s",
};
const BACKWARD_TURN_LEFT = {
  name: "BACKWARD_TURN_LEFT",
  keycode: [68, 83],
  key: "d+s",
};
const ONE_KEY_COMMANDS = [
  GO_FORWARDS,
  TURN_ON_SPOT_LEFT,
  GO_BACKWARDS,
  TURN_ON_SPOT_RIGHT,
  CLEAR_ACTION,
  TOGGLE_ACTION_GRABARM_GRAB_OBJECT,
  TOGGLE_ACTION_GRABARM_WEIGH_OBJECT,
  TOGGLE_ACTION_GRABARM_DEPOSIT_OBJECT,
  TOGGLE_ACTION_COLLECT_MINERAL,
  RETRACT_GRABARM,
  RESET_ARM,
  TOGGLE_MANUAL,
  CLEAR_TASK,
  TOGGLE_TASK_SCAN_QR_CODE,
  TOGGLE_TASK_FIND_CARD_SYMBOL,
  TOGGLE_TASK_RECOGNIZE_TEMPERATURE,
  TOGGLE_TASK_DANCING_ON_THE_MOON,
  TOGGLE_TASK_MOON_SURVIVAL,
  TOGGLE_TASK_MOON_MAZE,
  TOGGLE_TASK_MINERAL_ANALYSIS,
];
const MULTIPLE_KEY_COMMANDS = [
  FORWARD_TURN_LEFT,
  FORWARD_TURN_RIGHT,
  BACKWARD_TURN_RIGHT,
  BACKWARD_TURN_LEFT,
];

/**
 * keydown and keyup eventlistener, looks at keys that are pressed and compares them to all commands.
 * if a command is found, it sends this command to the socketserver, which will send it to the simulation
 * if a command is not found, it sends the command "NONE"
**/
window.addEventListener("keydown", function (event) {
  if (keys.includes(event.keyCode)) {
    return;
  }
  keys.push(event.keyCode);
  document.getElementById("keycode_pressed").innerHTML = keys;
  if (keys.length < 2) {
    for (let i = 0; i < ONE_KEY_COMMANDS.length; i++) {
      if (ONE_KEY_COMMANDS[i].keycode == keys) {
        document.getElementById("key_pressed").innerHTML =
          ONE_KEY_COMMANDS[i].name;
        send(ONE_KEY_COMMANDS[i].name);
        break;
      }
    }
  } else {
    let command = "NONE";
    for (let i = 0; i < MULTIPLE_KEY_COMMANDS.length; i++) {
      if (keys.length == MULTIPLE_KEY_COMMANDS[i].keycode.length) {
        keys.sort();
        MULTIPLE_KEY_COMMANDS[i].keycode.sort();
        if (
          JSON.stringify(MULTIPLE_KEY_COMMANDS[i].keycode) ===
          JSON.stringify(keys)
        ) {
            command = MULTIPLE_KEY_COMMANDS[i].name;
          break;
        }
      }
    }
    document.getElementById("key_pressed").innerHTML = command;
    send(command);
  }
});
window.addEventListener("keyup", function (event) {
  keys.splice(keys.indexOf(event.keyCode), 1);
  document.getElementById("keycode_pressed").innerHTML = keys;
  if (keys.length < 2) {
    for (let i = 0; i < ONE_KEY_COMMANDS.length; i++) {
      if (ONE_KEY_COMMANDS[i].keycode == keys) {
        document.getElementById("key_pressed").innerHTML =
          ONE_KEY_COMMANDS[i].name;
        send(ONE_KEY_COMMANDS[i].name);
        break;
      }
    }
  } else {
    let command = "NONE";
    for (let i = 0; i < MULTIPLE_KEY_COMMANDS.length; i++) {
      if (keys.length == MULTIPLE_KEY_COMMANDS[i].keycode.length) {
        keys.sort();
        MULTIPLE_KEY_COMMANDS[i].keycode.sort();
        if (
          JSON.stringify(MULTIPLE_KEY_COMMANDS[i].keycode) ===
          JSON.stringify(keys)
        ) {
          command = MULTIPLE_KEY_COMMANDS[i].name;
          break;
        }
      }
    }
    document.getElementById("key_pressed").innerHTML = command;
    send(command);
  }
  if (keys.length === 0) {
    document.getElementById("key_pressed").innerHTML = "NONE";
    send("NONE")
  }
});

/**
 * prevents sending a command multiple times,
 * also sends the command to the socket server
 * @param {string} command
 */
function send(command) {
  if (prev_command == command) {
    return;
  }
  prev_command = command;
  socket.send(`{"origin": "${ORIGIN}", "command": "${command}"}`);
}
/**
 * lists all possible commands with the keys that need to be pressed to use them
 */
function listcommands(){
  for(let i = 0; i < ONE_KEY_COMMANDS.length; i++){
    var li = document.createElement('li');
    li.appendChild(
      document.createTextNode(ONE_KEY_COMMANDS[i].key + " " + ONE_KEY_COMMANDS[i].name)
    );
    li.id = 'command';
    document.getElementById("possible_one_key_commands").appendChild(li);
  }
  for(let i = 0; i < MULTIPLE_KEY_COMMANDS.length; i++){
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(MULTIPLE_KEY_COMMANDS[i].key + " " + MULTIPLE_KEY_COMMANDS[i].name));
        li.id = "command";
        document.getElementById("possible_multiple_key_commands").appendChild(li);
  }
}
//fixme, find a better place
listcommands();
