const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';

const chatSocket = new WebSocket(
    protocol
    + window.location.host
    + '/ws/'
);

chatSocket.onmessage = function (e) {
    let data = JSON.parse(e.data);
    let t = $('#tableTickets').DataTable();
    let node = $(data.ticket).get(0);

    t.row.add(node).draw(false);
};

chatSocket.onclose = function (e) {
    console.error('Socket closed unexpectedly');
};