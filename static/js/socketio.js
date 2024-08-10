document.addEventListener("DOMContentLoaded", () => {

    var socket = io();

    socket.on('connect', function() {
        console.log("connected");
    });

    socket.on('message', (data) => {
        console.log(data);
    });

    chat_message = document.getElementById("chat_message");
    chat_button = document.getElementById("chat_button");


    chat_button.addEventListener("click", () => {
        console.log("clicked!")
        
    });
    
});
