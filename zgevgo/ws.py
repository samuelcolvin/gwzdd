from jsonfield.encoder import JSONEncoder
import os
import sys
import json
import zmq.green as zmq
from gevent import Timeout
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource, WebSocketError

THIS_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(THIS_DIR, '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zgevgo.settings')

import django
django.setup()

from zgevgo.basic.models import Action, Author

context = zmq.Context()

GET_ALL = 'get_all'
NEW_ACTION = 'new_action'


class ZmqApplication(WebSocketApplication):
    def __init__(self, ws=None):
        super(ZmqApplication, self).__init__(ws)
        # self.push_socket = context.socket(zmq.PUSH)
        # self.push_socket.connect('tcp://127.0.0.1:5557')
        # self.rep_socket = context.socket(zmq.REP)
        # self.rep_socket.connect('tcp://127.0.0.1:5558')
        # self.poller = zmq.Poller()
        # self.poller.register(self.rep_socket, zmq.POLLIN)
        self.methods = {
            GET_ALL: self.get_all,
            NEW_ACTION: self.new_action
        }

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
        pass
        # if not self.poller.poll():
        #     return
        # message = self.rep_socket.recv()
        # self.rep_socket.send('')
        # print 'zmq_receive:', message
        # try:
        #     self.ws.send(message)
        # except WebSocketError, e:
        #     print 'WebSocketError: %s' % e

    def on_open(self):
        print 'connection opened'

    def on_close(self, reason):
        pass
        # self.poller.unregister(self.rep_socket)
        # self.push_socket.close()
        # self.rep_socket.close()

    def on_message(self, message, *args, **kwargs):
        if message is None:
            return
        try:
            if message in self.methods:
                method_name, body = message, None
            else:
                method_name, body = message.split(':', 1)
            method = self.methods[method_name]
        except (ValueError, KeyError), e:
            self.ws.send('error: %s: %s' % (e.__class__.__name__, e))
            return

        method(body)
        # action = json.loads(message)
        # Action.objects.create(
        #     author=Author.objects.get_or_create(name=action['author'])[0],
        #     content=action['message'],
        #     stream_id=action['stream']
        # )

        # self.push_socket.send_json({'message': message})

    def get_all(self, body):
        stream_id = int(body)
        actions = Action.objects.filter(stream_id=stream_id).values('author__name', 'self_sha', 'timestamp', 'message')
        self.ws.send('actions:%s' % json.dumps(actions, cls=JSONEncoder))

    def new_action(self, body):
        print repr(body)
        action = json.loads(body)
        if set(action.keys()) != {'author', 'message', 'stream'}:
            self.ws.send('error: action has wrong keys: %r' % action.keys())
            return
        Action.objects.create(
            author=Author.objects.get_or_create(name=action['author'])[0],
            message=action['message'],
            stream_id=action['stream']
        )

resources = Resource(
    {'/': ZmqApplication}
)

if __name__ == '__main__':
    WebSocketServer(('', 8001), resources).serve_forever()
