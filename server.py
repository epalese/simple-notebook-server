import logging
import sys
import traceback
import json
import Queue
import signal
import contextlib
import StringIO

from twisted.internet import reactor
from twisted.python import log
from autobahn.twisted.websocket import WebSocketServerFactory
from autobahn.twisted.websocket import WebSocketServerProtocol

from threading import Thread

peers = []


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


class ServerProtocol(WebSocketServerProtocol):

    def __init__(self):
        super(ServerProtocol, self).__init__()
        self.namespace = {}
        self.queue = Queue.Queue(maxsize=0)
        self.executor = Thread(target=self.infinite_processing)

    def onConnect(self, request):
        logging.debug("WebSocket connection request from: {}".format(
            self.peer))
        logging.debug(request)
        peers.append(self)
        logging.debug("Peers after new connection: %s" % peers)
        self.executor.start()

    def onClose(self, wasClean, code, reason):
        log = "WebSocket connection for {} closed: {}"
        logging.debug(log.format(self.peer, reason))
        self.queue.put(None, True)
        peers.remove(self)
        logging.debug("Peers after closed connection: %s" % peers)

    def onMessage(self, message, isBinary):
        logging.debug("[%s] message: %s, isBinary: %s" % (
            self.peer, str(message), str(isBinary)))
        jmessage = json.loads(message)
        self.queue.put((jmessage, isBinary))

    def infinite_processing(self):
        logging.debug("[%s] starting infinite processing..." % (self.peer))
        while True:
            request = self.queue.get()
            if request is None:
                logging.debug("[%s] None found in queue. Terminating..." % (self.peer))
                return
            response = self.process(request)
            reactor.callFromThread(self.sendMessage, response[0], response[1])
            self.queue.task_done()
            logging.debug("[%s] inifinite_processing: processed" % (self.peer))

    def process(self, request):
        message = request[0]
        logging.debug("[%s] process> Processing message: %s" % (self.peer, message))
        with stdoutIO() as s:
            try:
                exec(message["code"], self.namespace)
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(
                    exc_type, exc_value, exc_traceback, file=s)
        output = json.dumps({
            "output": s.getvalue().encode('utf-8')
        })
        logging.debug("[%s] process> processing %s finished" % (self.peer, id))
        return (output, False)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Simple notebook server.')
    parser.add_argument(
        "-l", "--log",
        dest="logLevel",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level")
    args = parser.parse_args()
    if (args.logLevel):
        logging.basicConfig(level=getattr(logging, args.logLevel))
    # enable twisted logging
    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:3001")
    factory.protocol = ServerProtocol

    port = reactor.listenTCP(3001, factory)

    def signal_handler(signal, frame):
        import time
        print('[main] You pressed Ctrl+C!')
        for peer in peers:
            print("[main] Put none in %s queue" % peer)
            print("[main] Peer queue %s" % peer.queue)
            peer.queue.put(None, True)
        port.loseConnection()
        time.sleep(1)
        reactor.stop()
        print('[main] Everything has been shutdown!')
    signal.signal(signal.SIGINT, signal_handler)

    reactor.run()
