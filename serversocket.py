import socket
import select
import queue
import errno


class ServerSocket:
    def __init__(
            self,
            read_callback,
            max_connections,
            received_bytes):

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(False)
        self._socket.bind(('', 0))
        self.ip = self._socket.getsockname()[0]
        self.port = self._socket.getsockname()[1]
        self.callback = read_callback
        self._max_connections = max_connections
        self.received_bytes = received_bytes

    def run(self):
        self._socket.listen(self._max_connections)

        readers = [self._socket]
        writers = []

        queues = dict()
        IPs = dict()

        while readers:
            # Block until a socket is ready for processing.
            read, write, err = select.select(readers, writers, readers)

            for sock in read:
                if sock is self._socket:

                    client_socket, client_ip = self._socket.accept()

                    client_socket.setblocking(False)

                    readers.append(client_socket)

                    queues[client_socket] = queue.Queue()

                    IPs[client_socket] = client_ip
                else:

                    try:
                        data = sock.recv(self.received_bytes)
                    except socket.error as e:
                        if e.errno is errno.ECONNRESET:
                            data = None
                        else:
                            raise e
                    if data:

                        self.callback(IPs[sock], queues[sock], data)

                        if sock not in writers:
                            writers.append(sock)
                    else:

                        if sock in writers:
                            writers.remove(sock)

                        readers.remove(sock)

                        sock.close()

                        del queues[sock]

            for sock in write:
                try:
                    data = queues[sock].get_nowait()
                except queue.Empty:
                    writers.remove(sock)
                else:
                    sock.send(data)

            for sock in err:
                readers.remove(sock)
                if sock in writers:
                    writers.remove(sock)
                sock.close()
                del queues[sock]
