const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';

const ticketSocket = new WebSocket(
    protocol
    + window.location.host
    + '/ws/'
);

function onmessage(e) {
    let data = JSON.parse(e.data);
    let ticket = data.info;
    let t = $('#tableTickets').DataTable();
    let row = $(data.ticket)
    row.addClass('positive')
    let node = row.get(0);
    let sap_message = ticket.sap ? "SAP: " + ticket.sap : "";
    $.toast({
        class: 'success',
        title: "Поступила новая заявка №" + ticket.id,
        message: "Заказчик: " + ticket.customer + ' ' + sap_message,

    })
        ;
    t.row.add(node).draw(false);
};


function reconnect(e) {

    interval = setInterval(function () {
        localSocket = new WebSocket(
            protocol
            + window.location.host
            + '/ws/'
        );
        setTimeout(function () {

            if (localSocket.readyState === WebSocket.OPEN) {
                clearInterval(interval)
                localSocket.onmessage = function (e) {
                    onmessage(e);
                }
                localSocket.onclose = function (e) {
                    localSocket.close();
                    reconnect(e);
                }
                console.log('Reconnected!');
            }
            else {
                localSocket.close();
            }
        }, 2500);
    }
        , 5000);
};

ticketSocket.onmessage = function (e) {
    onmessage(e);
}

ticketSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly, reconnecting...');
    ticketSocket.close();
    reconnect(e);
}

