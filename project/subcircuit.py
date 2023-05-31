import matplotlib.pyplot as plt

import PySpice.Logging.Logging as Logging

logger = Logging.setup_logging()
from PySpice.Spice.Netlist import Circuit
from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Unit import *

import networkx as nx
import random
import re

# ##################### UTIL FUNCTIONS #####################
# hash a node name to a string
def hash_node_name(node_name, direction):
    # regex to remove all non-alphanumeric characters
    node_name = re.sub(r"\W+", "", node_name)
    result = node_name + direction
    # special case for input
    if result == "00in":
        return "input"
    else:
        return result

# hash the connections of an edge
def hash_edge_name(node1, node2):
    return hash_node_name(node1, "out"), hash_node_name(node2, "in")

##################### GENERATE CIRCUIT GRAPH #####################
# use networkx to generate a graph of the circuit
circuit_graph = nx.grid_graph(dim=[2, 2])

mst = nx.minimum_spanning_tree(circuit_graph)
print(mst.nodes)

# use node names to set the positions
pos = {}
for node in mst.nodes:
    pos[node] = node
# print(pos)

# randomly assign a value to each node
for node in mst.nodes:
    mst.nodes[node]["capacitance"] = random.randint(1, 5) * 1e-9

# each node is its own name
for node in mst.nodes:
    mst.nodes[node]["node_name"] = node.__str__()

labels = nx.get_node_attributes(mst, 'node_name')
print("node labels", len(labels))

# draw with node names and edge names
# nx.draw_networkx(mst, pos, with_labels=True, labels=labels, font_weight="bold")

# draw edge labels
edge_labels = nx.get_edge_attributes(mst, 'edge_name')
print("edge", mst.edges)
print("edge_labels", edge_labels)

# randomly assign a value to each edge
for edge in mst.edges:
    mst.edges[edge]["resistance"] = random.randint(1, 5)

##################### CONVERT GRAPH TO CIRCUIT #####################
libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)

# Voltage Pulse Configuration
startVoltage = 0 @ u_V
endVoltage = 1 @ u_V
startTime = 1 @ u_ns
riseTime = 1 @ u_us

circuit = Circuit("test")
circuit.PulseVoltageSource(
    "pulse", "input", circuit.gnd, startVoltage, endVoltage, startTime, riseTime
)

componenet_idx = 0

for node in mst.nodes:
    # get the node name
    node_name = mst.nodes[node]["node_name"]
    node_name_in = hash_node_name(node_name, "in")
    node_name_out = hash_node_name(node_name, "out")
    # each node is connected by its own in and out
    circuit.C(componenet_idx, node_name_in, node_name_out, mst.nodes[node]["capacitance"] @ u_F)
    componenet_idx += 1
    break

for edge in mst.edges:
    # get the edge name
    edge_name_first, edge_name_second = hash_edge_name(edge[0].__str__(), edge[1].__str__())
    # each edge, we create a resistor
    circuit.R(componenet_idx, edge_name_first, edge_name_second, mst.edges[edge]["resistance"] @ u_kΩ)
    componenet_idx += 1


# R1 = circuit.R(1, "2", "input", 4 @ u_kΩ)
# R2 = circuit.R(2,'p2','p6',1@u_kΩ)
# C2 = circuit.C(2, "input", "6", 1e-9 @ u_F)
# R3 = circuit.R(4, "5", "1", 1 @ u_kΩ)
# R4 = circuit.R(3, "6", "5", 1 @ u_kΩ)
# R5 = circuit.R(5, "0", "6", 1e-9 @ u_Ω)


print(str(circuit))
# exit(0)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=1e-11, end_time=100e-9)

print(analysis.nodes.values())
