function WebSocketConnection(){
  if (!('WebSocket' in window)) {
    alert('WebSockets are not supported by your browser.');
    return;
  }

  log('connecting...');
  var ws_url = $('#ws-url-ref').data('value');
  var stream = parseInt($('#stream-ref').data('value'));
  var ws = new WebSocket(ws_url);

  ws.onopen = function(){
    log('connected');
    ws.send('get_all:' + stream);
  };

  function Methods(){
    this.error = function(data){
      log('ERROR OCCURRED:' + data + '\n')
    };

    this.actions = function(raw_data){
      var json_data = raw_data.substr(raw_data.indexOf(':') + 1)
      var data = JSON.parse(json_data);
      log('actions: ' + data);
      console.log(data);
    };
  }
  var methods = new Methods();

  ws.onmessage = function (evt) {
    log('received: ' + evt.data);
    var method_data = evt.data.split(':');
    var method_name = method_data[0];
    if (typeof(methods[method_name]) == 'function'){
      methods[method_name](evt.data);
    }
  };

  ws.onclose = function () {
    log('Connection closed');
  };

  function send_message(){
    var msg = 'new_action:' + JSON.stringify({
      author: $('#author-input').val(),
      message: $('#message-input').val(),
      stream: stream
    });
    log('sending: '+ msg);
    ws.send(msg);
  }

  $('#send-msg').click(send_message);
}

var $console = $('#console');

function log(message){
  $console.prepend(message + '\n');
}

$(document).ready(function(){WebSocketConnection()});
