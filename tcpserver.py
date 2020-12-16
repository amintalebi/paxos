from serversocket import ServerSocket


class TCPServer:
    def __init__(self,
                 read_callback,
                 maximum_connections=5,
                 receive_bytes=2048):
        self.server_socket = ServerSocket(
            read_callback,
            maximum_connections,
            receive_bytes
        )

        self.ip = self.server_socket.ip
        self.port = self.server_socket.port

    def run(self):
        self.server_socket.run()
