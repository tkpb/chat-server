import multiprocessing
import socket

HOST = 'localhost'
PORT = 9000
MAX_CLIENTS = 5
BUF_SIZE = 1024
DEFAULT_ENCODING = 'ascii'
clients = []


def handle(connection, address):
    if len(clients) >= MAX_CLIENTS:
        connection.sendall("Server is full!".encode(DEFAULT_ENCODING))
        connection.close()
    else:
        clients.append('User' + str(len(clients) + 1))
        import logging
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger("user%r" % address[1])
        try:
            logger.debug("Connected %r at %r", connection, address)
            while True:
                data = connection.recv(BUF_SIZE).decode(DEFAULT_ENCODING)
                if data == "":
                    logger.debug("Socket closed remotely")
                    break
                logger.debug("Received data %r", data)
                connection.sendall(data.encode(DEFAULT_ENCODING))
                logger.debug("Sent data")
        except:
            logger.exception("Problem handling request")
        finally:
            logger.debug("Closing socket")
            connection.close()


class Server(object):
    def __init__(self, hostname, port):
        import logging
        self.logger = logging.getLogger("server")
        self.hostname = hostname
        self.port = port

    def start(self):
        self.logger.debug("listening")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        while True:
            conn, address = self.socket.accept()
            self.logger.debug("Got connection")
            process = multiprocessing.Process(target=handle, args=(conn, address))
            process.daemon = True
            process.start()
            self.logger.debug("Started process %r", process)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    server = Server(HOST, PORT)
    try:
        logging.info("Listening")
        server.start()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")
