from node import Node

import threading

f = open("input", 'r')
lines = f.readlines()


n = int(lines[0])

nodes = {}

for i in range(1, n+1):
    nodes[i] = Node(uid=i, network_size=n)

uid = -1
for i in range((n * n) + 1):
    if len(lines[i].split()) == 4:
        tokens = lines[i].split()
        uid = int(tokens[0])
        nodes[uid].start_delay = int(tokens[1])
        nodes[uid].potential_leader_time_out = int(tokens[2])
        nodes[uid].propose_time_out = int(tokens[3])
    elif len(lines[i].split()) == 2:
        tokens = lines[i].split()
        address = nodes[int(tokens[0])].address
        nodes[uid].stream.add_sender(address, float(tokens[1]))
        nodes[uid].outgoing_addresses[int(tokens[0])] = address


for node in nodes.values():
    threading.Thread(target=node.run).start()
