import gevent
import random
import zmq.green as zmq


def pull():
    pull_socket = context.socket(zmq.PULL)
    pull_socket.bind('tcp://127.0.0.1:5557')

    while True:
        message = pull_socket.recv()
        print 'got message: %s' % message
        gevent.sleep(0)


def push():
    req_socket = context.socket(zmq.REQ)
    req_socket.bind('tcp://127.0.0.1:5558')
    pollout = zmq.Poller()
    pollout.register(req_socket, zmq.POLLOUT)
    pollin = zmq.Poller()
    pollin.register(req_socket, zmq.POLLIN)

    i = 1
    while True:
        if pollout.poll():
            print 'send message %d' % i,
            req_socket.send('new_message: %d' % i)
            if pollin.poll():
                print 'received %r' % req_socket.recv()
            else:
                print ''
            i += 1
        gevent.sleep(random.random())

context = zmq.Context()
gevent.joinall([
    gevent.spawn(pull),
    gevent.spawn(push),
])
