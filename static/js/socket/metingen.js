const ORIGIN = 'client';
const BROADCASTER = 'webots';

const COLOR_ACTIVE = '#f96d00';
const COLOR_INACTIVE = '#505050';

const RECOGNIZE_CARD_SYMBOL = "Finding Card Symbol";
const RECOGNIZE_TEMPERATURE = "Measuring Temperature of Water Source";
const MINERAL_ANALYSIS = "Mineral Analysis";

const TASKS =
    [
        {
            task: RECOGNIZE_TEMPERATURE,
            class: "Recognize-Temperature",
            topics: [
                {
                    name: "Temperature",
                    id: "temperature"
                }
            ]
        },
        {
            task: MINERAL_ANALYSIS,
            class: "Mineral-Analysis",
            topics: [
                {
                    name: "Weight",
                    id: "weight"
                }
            ]
        },
        {
            task: RECOGNIZE_CARD_SYMBOL,
            class: "Recognize-Card-Symbol",
            topics: [
                {
                    name: "Card Symbol",
                    id: "card-symbol"
                }
            ]
        }
    ];


function getTaskFromName(task_name) {
    for (let i = 0; i < TASKS.length; i++) {
        if (TASKS[i].task == task_name) {
            return TASKS[i];
        }
    }
    return 'None'
}

let task_data_div = null

var socket = null;

const SOCKET_CONNECTED_BAR = document.getElementById('socket-connected');
const CURRENT_TASK_ELEM = document.getElementById('task_value');
const CURRENT_STAGE_ELEM = document.getElementById('stage_value');
let current_task = CURRENT_TASK_ELEM.innerText;
let current_stage = CURRENT_STAGE_ELEM.innerText;

function connect_socket(conn) {
    SOCKET_CONNECTED_BAR.style.background = COLOR_INACTIVE;

    task_data_div = document.getElementById('task-data');

    TASKS.forEach(TASK => {
        TASK.topics.forEach(topic => {
            task_data_div.innerHTML += `
                <div id="${topic.id}" class="data ${TASK.class}">
                    <div class="top-line" style="background: ${COLOR_INACTIVE};">
                    </div>
                    <div class="topic-container">
                        <h1>${topic.name}</h1>
                    </div><br><br>
                    <div class="value-container">
                    </div>
                </div>
            `;
        });
    });


    // Create WebSocket connection.
    socket = new WebSocket(conn);

    socket.onerror = function (event) {
        SOCKET_CONNECTED_BAR.style.background = COLOR_INACTIVE;
    };

    // Connection opened
    socket.addEventListener('open', function (event) {
        socket.send(JSON.stringify({ origin: 'client' }));
        SOCKET_CONNECTED_BAR.style.background = COLOR_ACTIVE;
    });

    // Listen for messages
    socket.addEventListener('message', function (event) {
        json = JSON.parse(event.data);
        if (!json.origin || json.origin != BROADCASTER) return;
        //console.log(`Message from ${json.origin}`);

        if (current_task != json.task) {
            current_task = json.task
            CURRENT_TASK_ELEM.innerHTML = current_task;
            decode(CURRENT_TASK_ELEM, 2, 5);
            reset();
        }
        if (current_stage != json.stage) {
            current_stage = json.stage
            CURRENT_STAGE_ELEM.innerHTML = current_stage;
            decode(CURRENT_STAGE_ELEM, 2, 5);
        }

        let task = getTaskFromName(json.task);

        updateHTML(task, json)
    });

    socket.addEventListener('close', function (event) {
        console.log('Connection Closed ', event.data);
        SOCKET_CONNECTED_BAR.style.background = COLOR_INACTIVE;
    });
}

function reset() {
    task_data_div.innerHTML = '';
    TASKS.forEach(TASK => {
        TASK.topics.forEach(topic => {
            task_data_div.innerHTML += `
                <div id="${topic.id}" class="data ${TASK.class}">
                    <div class="top-line" style="background: ${COLOR_INACTIVE};">
                    </div>
                    <div class="topic-container">
                        <h1>${topic.name}</h1>
                    </div><br><br>
                    <div class="value-container">
                    </div>
                </div>
            `;
        });
    });
}

function disconnect_socket() {
    if (socket) { socket.close(); }
    socket = null;
}

function arrangeElement(elem) {
    if (elem.parentNode.firstChild.nextElementSibling.className == elem.className) {
        return
    }
    elem.parentNode.insertBefore(elem, elem.parentNode.firstChild);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const ANIMATION_TIME = 500

async function updateHTML(task, json_data, reset = false) {
    let div = false
    if (json_data.topic.length > 0) {
        div = task_data_div.querySelector(`#${json_data.topic.replace(/\s+/g, '-')}`);
    }
    switch (task.task) {
        case RECOGNIZE_TEMPERATURE:
            updateRecognizeTemperature(div, json_data);
            break;
        case MINERAL_ANALYSIS:
            updateMineralAnalysis(div, json_data);
            break;
        case RECOGNIZE_CARD_SYMBOL:
            updateSymbolRecognition(div, json_data);
            break;
    }
    if (div) {
        await sleep(ANIMATION_TIME)
        if (div) {
            arrangeElement(div)
        }
    }
}

function updateRecognizeTemperature(div, json_data) {
    switch (json_data.topic) {
        case "Temperature":
            let topic_container = div.querySelector('.topic-container');
            let value_container = div.querySelector('.value-container');
            let colored_line = div.querySelector('.top-line');

            topic_container.innerHTML = `<h1>${json_data.topic}</h1>`;
            let color = ''
            switch (json_data.value) {
                case 'Cold': color = '#00eaff'; break;
                case 'Lukewarm': color = '#ffc800'; break;
                case 'Warm': color = '#ff8c00'; break;
                case "Hot": color = '#ff0000'; break;
            }
            value_container.innerHTML = `<p>${json_data.value}</p>`;
            colored_line.style.background = color
            colored_line.style.boxShadow = `0 0 15px ${color}`;
            decode(value_container.querySelector('p'), 5, 10);
            break;
    }
}

function updateMineralAnalysis(div, json_data) {
    switch (json_data.topic) {
        case "Weight":
            let topic_container = div.querySelector('.topic-container');
            let value_container = div.querySelector('.value-container');
            let colored_line = div.querySelector('.top-line');
            colored_line.style.background = COLOR_ACTIVE;

            topic_container.innerHTML = `<h1>${json_data.topic}</h1>`;
            value_container.innerHTML = `<p>${json_data.value} KG</p>`;
            colored_line.style.background = COLOR_ACTIVE
            colored_line.style.boxShadow = `0 0 15px ${COLOR_ACTIVE}`;
            decode(value_container.querySelector('p'), 5, 10);
            break;
    }
}

function updateSymbolRecognition(div, json_data) {
    switch (json_data.topic) {
        case "Card Symbol":
            let topic_container = div.querySelector('.topic-container');
            let value_container = div.querySelector('.value-container');
            let colored_line = div.querySelector('.top-line');
            colored_line.style.background = COLOR_ACTIVE;

            topic_container.innerHTML = `<h1>${json_data.topic}</h1>`;
            let symbol = `./static/media/live/card-symbols/${json_data.value}.png`;
            value_container.innerHTML = `<div style="display: flex; justify-content: center;">
                                            <img style="width: 3.5em; height: auto;position:absolute;margin-top:-0.4em" src="${symbol.toLowerCase()}" class="img-fluid">
                                            <span style="font-size: 1.5em; position:absolute;letter-spacing: 0.1em; text-shadow: 0 0 3px black;">${json_data.value}</span>
                                        </div>`;
            colored_line.style.background = COLOR_ACTIVE
            colored_line.style.boxShadow = `0 0 15px ${COLOR_ACTIVE}`;
            decode(value_container.querySelector('p'), 5, 10);
            break;
    }
}