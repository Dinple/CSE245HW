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
    return result
    # special case for input
    # if result == "00in":
    #     return "input"
    # else:
    #     return result


# hash the connections of an edge
def hash_edge_name(node1, node2):
    return hash_node_name(node1, "in"), hash_node_name(node2, "in")


##################### GENERATE CIRCUIT GRAPH #####################
# use networkx to generate a graph of the circuit
circuit_graph = nx.grid_graph(dim=[2, 6])

mst = nx.minimum_spanning_tree(circuit_graph, algorithm="prim")
print(mst.nodes)

# use node names to set the positions
pos = {}
for node in mst.nodes:
    pos[node] = node
# print(pos)

# randomly assign a value to each node
for node in mst.nodes:
    mst.nodes[node]["capacitance"] = random.randint(1, 2)

# each node is its own name
for node in mst.nodes:
    mst.nodes[node]["node_name"] = node.__str__()

labels = nx.get_node_attributes(mst, "node_name")
print("node labels", len(labels))

# draw with node names and edge names
nx.draw_networkx(mst, pos, with_labels=True, labels=labels, font_weight="bold")
plt.show()

# draw edge labels
edge_labels = nx.get_edge_attributes(mst, "edge_name")
print("edge", mst.edges)
print("edge_labels", edge_labels)

# randomly assign a value to each edge
for edge in mst.edges:
    mst.edges[edge]["resistance"] = random.randint(1, 2)

##################### CONVERT GRAPH TO CIRCUIT #####################
libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)

period = 50 @ u_ns
pulse_width = period / 2

# Voltage Pulse Configuration
startVoltage = 0 @ u_V
endVoltage = 1 @ u_V
riseTime = 100 @ u_ps
fallTime = 100 @ u_ps

circuit = Circuit("test")
circuit.PulseVoltageSource(
    "clock",
    "51in",
    circuit.gnd,
    initial_value=startVoltage,
    pulsed_value=endVoltage,
    pulse_width=pulse_width,
    period=period,
    rise_time=riseTime,
    fall_time=fallTime,
)

componenet_idx = 0

for node in mst.nodes:
    # get the node name
    node_name = mst.nodes[node]["node_name"]
    node_name_in = hash_node_name(node_name, "in")
    # node_name_out = hash_node_name(node_name, "out")
    # each node is connected by its own in and out
    circuit.C(
        componenet_idx, node_name_in, circuit.gnd, mst.nodes[node]["capacitance"] @ u_pF
    )
    componenet_idx += 1

for edge in mst.edges:
    # get the edge name
    edge_name_first, edge_name_second = hash_edge_name(
        edge[0].__str__(), edge[1].__str__()
    )
    # each edge, we create a resistor
    circuit.R(
        componenet_idx,
        edge_name_first,
        edge_name_second,
        mst.edges[edge]["resistance"] @ u_kΩ,
    )
    componenet_idx += 1

# C1 = circuit.C(1, "input", circuit.gnd, 1e-9 @ u_F)
# R1 = circuit.R(2, "input", "c2in", 1 @ u_kΩ)
# C2 = circuit.C(3, "c2in", circuit.gnd, 1e-9 @ u_F)
# R2 = circuit.R(4, "c2in", "c3in", 1 @ u_kΩ)
# C3 = circuit.C(5, "c3in", circuit.gnd, 1e-9 @ u_F)


print(str(circuit))
# exit(0)
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=period/1e5, end_time=period*2)

# plot
figure, ax = plt.subplots(figsize=(20, 10))
ax.grid()
ax.set_xlabel("Time [s]")
ax.set_ylabel("Voltage [V]")
plt.plot(analysis["51in"])
plt.plot(analysis["41in"])
plt.plot(analysis["31in"])
plt.plot(analysis["21in"])
plt.plot(analysis["11in"])

ax.legend(["51in", "41in", "31in", "21in", "11in"])
plt.show()
