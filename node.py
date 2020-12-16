import json
import threading
import sys
from message import Message, make_msg
from stream import Stream


class Node:

    def __init__(self,
                 uid=None,
                 network_size=0):

        ''' Network Variables '''
        self.stream = Stream()
        self.address = (self.stream.ip, self.stream.port)
        self.outgoing_addresses = {}
        self.network_size = network_size

        ''' Algorithm Variables '''
        self.uid = uid
        self.stored_value = -1
        self.ticket = 0
        self.max = 0
        self.proposed_value = self.max
        self.store = 0

        self.start_delay = 0
        self.potential_leader_time_out = 0
        self.propose_time_out = 0
        self.state = "IDLE"

        self.POTENTIAL_LEADER_ACK_SET = set()
        self.V_PROPOSE_ACK_SET = set()

        print('peer initialized successfully')

    def run(self):
        threading.Timer(self.start_delay, self.potential_leader).start()
        while True:
            stream_in_buff = self.stream.read_in_buf()
            for message in stream_in_buff:
                try:
                    message = Message(**json.loads(message.decode(encoding='utf-8')))
                    self.handle_message(message)
                except json.decoder.JSONDecodeError:
                    pass

    def handle_message(self, message):
        print('node', self.uid, ": ", message)

        if message.type == "POTENTIAL_LEADER_ACK":
            if self.state == "POTENTIAL_LEADER":
                self.POTENTIAL_LEADER_ACK_SET.add(message)
        elif message.type == "POTENTIAL_LEADER":
            if message.ticket > self.max:
                self.max = message.ticket
                msg = make_msg(type="POTENTIAL_LEADER_ACK", ticket=self.store, nid=self.uid, value=self.stored_value)
                self.stream.add_message_to_out_buff(self.outgoing_addresses[message.nid], msg)
                self.stream.send_messages()
        elif message.type == "V_PROPOSE":
            if message.ticket == self.max:
                self.stored_value = message.value
                self.store = message.ticket
                msg = make_msg(type="V_PROPOSE_ACK", ticket=-1, nid=self.uid, value=-1)
                self.stream.add_message_to_out_buff(self.outgoing_addresses[message.nid], msg)
                self.stream.send_messages()
        elif message.type == "V_PROPOSE_ACK":
            if self.state == "V_PROPOSE":
                self.V_PROPOSE_ACK_SET.add(message)
        elif message.type == "V_DECIDE":
            self.stored_value = message.value
            print("node ", self.uid, " DECIDED ", self.stored_value)

    def check_votes(self):
        if not len(self.POTENTIAL_LEADER_ACK_SET) >= self.network_size // 2 + 1:
            self.state = "IDLE"
            self.POTENTIAL_LEADER_ACK_SET.clear()
            return

        self.state = "V_PROPOSE"
        max_store = 0
        v = -1
        nids = []
        for vote in self.POTENTIAL_LEADER_ACK_SET:
            nids.append(vote.nid)
            if vote.ticket > max_store:
                max_store = vote.ticket
                v = vote.value

        if max_store > 0:
            self.proposed_value = v

        v_propose = make_msg(type="V_PROPOSE", ticket=self.ticket, nid=self.uid, value=self.proposed_value)
        for nid in nids:
            self.stream.add_message_to_out_buff(self.outgoing_addresses[nid], v_propose)
        threading.Timer(self.propose_time_out, self.check_votes_second_round).start()
        self.stream.send_messages()

        self.POTENTIAL_LEADER_ACK_SET.clear()

    def check_votes_second_round(self):
        if not len(self.V_PROPOSE_ACK_SET) >= self.network_size // 2 + 1:
            self.state = "IDLE"
            self.V_PROPOSE_ACK_SET.clear()
            return

        self.state = "DECIDE"

        v_decide = make_msg(type="V_DECIDE", ticket=self.ticket, nid=self.uid, value=self.proposed_value)
        for outgoing in self.outgoing_addresses.values():
            self.stream.add_message_to_out_buff(outgoing, v_decide)
        self.stream.send_messages()
        self.V_PROPOSE_ACK_SET.clear()

    def potential_leader(self):
        self.state = "POTENTIAL_LEADER"
        self.ticket = self.max + 1
        propose_msg = make_msg(type="POTENTIAL_LEADER", ticket=self.ticket, nid=self.uid, value=-1)
        for outgoing in self.outgoing_addresses.values():
            self.stream.add_message_to_out_buff(outgoing, propose_msg)
        threading.Timer(self.potential_leader_time_out, self.check_votes).start()
        self.stream.send_messages()
