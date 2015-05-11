from gevent import Timeout
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource, WebSocketError
import zmq.green as zmq

context = zmq.Context()


class ZmqApplication(WebSocketApplication):
    def __init__(self, ws=None):
        print '__init__'
        super(ZmqApplication, self).__init__(ws)
        self.push_socket = context.socket(zmq.PUSH)
        self.push_socket.connect('tcp://127.0.0.1:5557')
        self.rep_socket = context.socket(zmq.REP)
        self.rep_socket.connect('tcp://127.0.0.1:5558')
        self.poller = zmq.Poller()
        self.poller.register(self.rep_socket, zmq.POLLIN)

    def handle(self):
        self.protocol.on_open()

        i = 0
        while True:
            stop = None
            if i % 2:
                with Timeout(0.1, False):
                    stop = self.ws_receive()
            else:
                self.zmq_receive()
            if stop:
                print 'stopping'
                break
            i += 1

    def ws_receive(self):
        try:
            message = self.ws.receive()
        except WebSocketError:
            self.protocol.on_close()
            return True
        self.protocol.on_message(message)

    def zmq_receive(self):
        if not self.poller.poll():
            return
        message = self.rep_socket.recv()
        self.rep_socket.send('')
        print 'zmq_receive:', message
        try:
            self.ws.send(message)
        except WebSocketError, e:
            print 'WebSocketError: %s' % e

    def on_open(self):
        print 'connection opened'

    def on_message(self, message, *args, **kwargs):
        print 'on_message:', message
        if message is None:
            return
        self.push_socket.send_json({'message': message})
        # self.ws.send(message)

    def on_close(self, reason):
        print 'on_close, reason: ', reason
        self.poller.unregister(self.rep_socket)
        self.push_socket.close()
        self.rep_socket.close()

resources = Resource(
    {'/': ZmqApplication}
)

if __name__ == '__main__':
    WebSocketServer(('', 8001), resources).serve_forever()
