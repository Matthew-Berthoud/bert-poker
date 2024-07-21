var socket = io();

socket.on('connect', function() {
    console.log("connected");
});

socket.on('message', (data) => {
    console.log(data);
});

