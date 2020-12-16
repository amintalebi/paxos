import threading

from sender import Sender
from tcpserver import TCPServer


class Stream:
    def __init__(self):
        self.senders = {}

        self._server_in_buf = []

        def callback(address, queue, data):
            queue.put(bytes('ACK', 'utf8'))
            self._server_in_buf.append(data)

        self.tcp_server = TCPServer(read_callback=callback)
        server_thread = threading.Thread(target=self.tcp_server.run)
        server_thread.start()

        self.ip = Sender.parse_ip(self.tcp_server.ip)
        self.port = Sender.parse_port(self.tcp_server.port)

    def get_server_address(self):
        return self.ip, self.port

    def clear_in_buff(self, snapshot_size):
        self._server_in_buf = self._server_in_buf[snapshot_size:]

    def add_sender(self, server_address, delay):
        self.senders[tuple(server_address)] = Sender(server_address=server_address, delay=delay)

    def add_message_to_out_buff(self, server_address, message):
        self.senders[tuple(server_address)].add_message_to_out_buff(message)

    def read_in_buf(self):
        stream_in_buff_snapshot = self._server_in_buf
        snapshot_size = len(stream_in_buff_snapshot)
        self.clear_in_buff(snapshot_size)
        return stream_in_buff_snapshot

    def send_messages(self):

        for sender in self.senders.values():
            try:
                sender.send_message()
            except IOError as e:
                print(e)
