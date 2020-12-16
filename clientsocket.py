import socket
import sys


class ClientSocket:
    def __init__(self, mode, port, received_bytes=2048):
        self.connect_ip = mode

        self.connect_port = port
        if type(self.connect_port) != int:
            print("port must be an integer", file=sys.stderr)
            raise ValueError

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.received_bytes = received_bytes
        self._socket.connect((self.connect_ip, self.connect_port))
        self.closed = False

    def get_port(self):
        return self.connect_port

    def get_ip(self):
        return self.connect_ip

    def send(self, data):
        if type(data) == str:
            data = bytes(data, "UTF-8")

        if type(data) != bytes:
            print("data must be a string or bytes", file=sys.stderr)
            raise ValueError

        self._socket.send(data)
        response = self._socket.recv(self.received_bytes)
        return response

    def close(self):
        if not self.closed:
            self._socket.close()
            self.closed = True
