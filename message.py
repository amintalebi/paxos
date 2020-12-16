import json


class Message:
    def __init__(self, type, ticket, value, nid):
        self.type = type
        self.value = value
        self.nid = nid
        self.ticket = ticket

    def __str__(self):
        return "type: " + str(self.type) + ", nid: " + str(self.nid) + ", ticket: " + str(self.ticket) + ", value: " + str(self.value)


def make_msg(type, ticket, value, nid):
    message = Message(type, ticket, value, nid)
    return json.dumps(message.__dict__).encode('utf-8')


