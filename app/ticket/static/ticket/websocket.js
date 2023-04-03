const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';

const chatSocket = new WebSocket(
    protocol
    + window.location.host
    + '/ws/'
);

chatSocket.onmessage = function (e) {
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

chatSocket.onclose = function (e) {
    console.error('Socket closed unexpectedly');
};