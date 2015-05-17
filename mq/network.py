import time
import random
from multiprocessing import Process
import zmq.green as zmq
import gevent
from threading import Thread

# each node is identified by it's port
NODES = range(50)


class TimeoutException(Exception):
    pass


def get_port(node_id):
    return 16000 + node_id


# server_address_base = 'tcp://*:%d'
# client_address_base = 'tcp://localhost:%d'

server_address_base = 'ipc:///tmp/feeds_%d'
client_address_base = server_address_base


class Node(object):
    def __init__(self, node_id):
        self.node_id = node_id
        self.shared_job_no = 0
        self.go = True

    def run_gevent(self):
        ctx = zmq.Context()
        print 'starting %s' % self.node_id
        g = gevent.spawn(self.server, ctx, self.node_id)
        self.client(ctx, self.node_id)
        print '%d node: client finished' % self.node_id
        gevent.sleep(5)
        self.go = False
        g.kill()
        # print '%d node: exiting' % self.node_id

    def run_threading(self):
        ctx = zmq.Context()
        print 'starting %s' % self.node_id
        Thread(target=self.server, args=(ctx, self.node_id)).start()
        self.client(ctx, self.node_id)
        gevent.sleep(5)
        self.go = False
        print '%d node: client finished' % self.node_id

    def server(self, ctx, node_id):
        rep_socket = ctx.socket(zmq.REP)
        rep_socket.bind(server_address_base % get_port(node_id))
        rep_socket.set_hwm(100000)
        timeout = gevent.Timeout(2, TimeoutException)
        start = time.time()
        new_messages = 0
        while True:
            if not self.go:
                break
            if not rep_socket.poll(1000):
                continue
            timeout.start()
            try:
                message = rep_socket.recv_json()
                rep_socket.send('OK %r' % message)
            except TimeoutException:
                pass
            else:
                new_messages += 1
            finally:
                timeout.cancel()
            if (time.time() - start) > 1:
                if node_id % 10 == 0:
                    print 'node %d: server msg count %d, job_no: %d' % (node_id, new_messages, self.shared_job_no)
                start = time.time()
                new_messages = 0

    def client(self, ctx, this_node_id):
        timeout = gevent.Timeout(10, TimeoutException)
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
                    print 'timeout on node %d client, job %d' % (this_node_id, job_no)
                    return
                finally:
                    timeout.cancel()
                    socket.close()
            self.shared_job_no = job_no
            gevent.sleep(0.1 + random.random()*0.1)


def run_node(node_id):
    # Node(node_id).run_threading()
    Node(node_id).run_gevent()

if __name__ == '__main__':
    for node_id in NODES:
        Process(target=run_node, args=(node_id,)).start()
    print 'started %d nodes' % len(NODES)
