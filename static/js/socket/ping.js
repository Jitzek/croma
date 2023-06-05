function ping(ip, port, onPinging, onOnline, onOffline) {
    onPinging();
    // Create WebSocket connection.
    const socket = new WebSocket(`ws://${ip}:${port}`);
    socket.addEventListener('message', function () {
        onOnline();
        socket.close();
    });
    socket.addEventListener('error', function (e) {
        onOffline();
        socket.close();
    });
}