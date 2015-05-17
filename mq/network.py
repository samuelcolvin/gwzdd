import time
import random
import zmq.green as zmq
import gevent
from threading import Thread

# each node is identified by it's port
NODES = range(20)


class TimeoutException(Exception):
    pass


def get_port(node_id):
    return 16000 + node_id


server_address_base = 'tcp://*:%d'
client_address_base = 'tcp://localhost:%d'

server_address_base = 'ipc:///tmp/feeds_%d'
client_address_base = server_address_base


def server(ctx, node_id, shared):
    rep_socket = ctx.socket(zmq.REP)
    rep_socket.bind(server_address_base % get_port(node_id))
    rep_socket.set_hwm(100000)
    timeout = gevent.Timeout(2, TimeoutException)
    start = time.time()
    new_messages = 0
    while True:
        if not rep_socket.poll(1000):
            continue
        timeout.start()
        try:
            message = rep_socket.recv_json()
            rep_socket.send('OK %r' % message)
        except TimeoutException:
            pass
        finally:
            timeout.cancel()
        new_messages += 1
        if (time.time() - start) > 1:
            if node_id % 10 == 0:
                print 'node %d: server msg count %d, job_no: %d' % (node_id, new_messages, shared['job_no'])
            start = time.time()
            new_messages = 0
        gevent.sleep(0)


def client(ctx, this_node_id, shared):
    timeout = gevent.Timeout(5, TimeoutException)
    for job_no in range(100):
        for node_id in NODES:
            if node_id == this_node_id:
                continue
            socket = ctx.socket(zmq.REQ)
            socket.set_hwm(100000)
            timeout.start()
            try:
                socket.connect(client_address_base % get_port(node_id))
                socket.send_json({'source': this_node_id, 'job_no': job_no})
                socket.recv()
            except TimeoutException:
                # this normally only happens at the end of a run
                print 'timeout on node %d client, job %d, killing client' % (this_node_id, job_no)
                return
            finally:
                timeout.cancel()
                socket.close()
        shared['job_no'] = job_no
        gevent.sleep(0.05 + random.random()*0.05)


def run_node(node_id):
    ctx = zmq.Context()
    print 'starting %s' % node_id
    shared = {'job_no': 0}
    g = gevent.spawn(server, ctx, node_id, shared)
    client(ctx, node_id, shared)
    print '%d node: client finished' % node_id
    gevent.sleep(5)
    g.kill()
    print '%d node: exiting' % node_id

if __name__ == '__main__':
    for node_id in NODES:
        Thread(target=run_node, args=(node_id,)).start()
    print 'started %d nodes' % len(NODES)
