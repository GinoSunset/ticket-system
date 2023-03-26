
const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/'
);

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data);
};

chatSocket.onclose = function (e) {
    console.error('Socket closed unexpectedly');
};