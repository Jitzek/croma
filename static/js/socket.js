// Create WebSocket connection.
const socket = new WebSocket('ws://localhost:4444');
socket.onerror = function (event) {
    console.log(event.data);
 };
// Connection opened
socket.addEventListener('open', function (event) {
    socket.send(JSON.stringify({origin: 'client'}));
});

// Listen for messages
socket.addEventListener('message', function (event) {
    json = JSON.parse(event.data);
    console.log(`Message from ${json['origin']}`);
    json['keys'].forEach(key => {
        console.log(`${key['key']}: ${key['value']}`);
    });
});

socket.addEventListener('close', function (event) {
    console.log('Connection Closed ', event.data);
});