function WebSocketConnection(){
  if (!('WebSocket' in window)) {
    alert('WebSocket NOT supported by your Browser!');
    return;
  }
  var ws = null;

  function connect() {
    log('connecting...');
    ws = new WebSocket(ws_url);

    ws.onopen = function(){
      log('connected');
    };

    ws.onmessage = function (evt) {
      log('received: ' + evt.data);
    };

    ws.onclose = function () {
      log('Connection closed');
    };
  }

  function send_message(){
    var msg = $('#message-box').val();
    log('sending: '+ msg);
    ws.send(msg);
  }

  $('#open').click(connect);
  $('#send-msg').click(send_message);
  $('#close').click(function(){
    log('closing connection');
    ws.close()
  });
}

var $console = $('#console');

function log(message){
  $console.prepend(message + '\n');
}

$(document).ready(function(){WebSocketConnection()});
