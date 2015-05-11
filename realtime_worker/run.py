import time
import zmq
import threading
import random


class StoppableThread(threading.Thread):
    def __init__(self):
        super(StoppableThread, self).__init__()
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class PullThread(StoppableThread):
    def run(self):
        pull_socket = context.socket(zmq.PULL)
        pull_socket.bind('tcp://127.0.0.1:5557')

        while True:
            message = pull_socket.recv()
            if message != 'hb':
                print 'message: %r' % message
            if self.stopped():
                break


class PushThread(StoppableThread):
    def run(self):
        push_socket = context.socket(zmq.PUSH)
        push_socket.bind('tcp://127.0.0.1:5558')

        i = 1
        while True:
            time.sleep(random.random()*0.1)
            push_socket.send('new_message: %d' % i)
            i += 1
            if self.stopped():
                break


context = zmq.Context()
threads = [
    PullThread(),
    PushThread()
]
[t.start() for t in threads]

while True:
    go = True
    try:
        resp = raw_input('enter "x" to stop\n')
    except KeyboardInterrupt:
        go = False
    else:
        if resp.lower() == 'x':
            go = False
    if not go:
        print 'stopping'
        [t.stop() for t in threads]
        break
