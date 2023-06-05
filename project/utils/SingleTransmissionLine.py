import matplotlib.pyplot as plt
import numpy as np
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from utils.Utils import get_delay_slew
class SingleTransmissionLine_Generator():
    def __init__(self, name, num_stages, value_R, value_C):
        '''
        :param name: name of your circuit
        :param num_stages: stages of RC transmission line model
        :param value_R: shape: [#stages]; unit: kOhm
        :param value_C: shape: [#stages]; unit: pF
        '''
        self.name = name
        self.circuit = Circuit(name)
        self.res_unit = 1@u_kΩ
        self.cap_unit = 1@u_pF
        self.time_unit = 1@u_ns
        self.num_stages = num_stages
        self.Rs = value_R
        self.Cs = value_C
        self.in_slew = 0
        self.in_waveform = None
        self.out_waveform = None
        self.time_trace = None
    def build(self, silent=True):
        '''
        build a circuit object
        input node name == 'node 0'
        output node name == 'node #stage'
        '''
        for i in range(self.num_stages):
            self.circuit.R(i, 'node'+str(i), 'node'+str(i+1), self.Rs[i]*self.res_unit)
            self.circuit.C(i, 'node'+str(i+1), self.circuit.gnd, self.Cs[i]*self.cap_unit)
        if not silent:
            print('Check the built circuit')
            print(self.circuit)
    def simulate(self, rise_time, pulse_period, precision = 20, show=False):
        '''
        simulate the circuit, save the waveform, get the time step size
        '''
        self.circuit.PulseVoltageSource('clock', 'node0', self.circuit.gnd, initial_value=1@u_V, pulsed_value=0@u_V,
                                   pulse_width=(pulse_period*self.time_unit)/2, period=pulse_period*self.time_unit,
                                   rise_time=rise_time*self.time_unit, fall_time=rise_time*self.time_unit,
                                   delay_time = -rise_time*self.time_unit)
        simulator = self.circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.transient(step_time=self.time_unit/precision, end_time=(pulse_period-rise_time)*self.time_unit)
        output_node = 'node' + str(self.num_stages)
        self.in_slew = rise_time
        self.in_waveform = analysis.nodes['node0']
        self.out_waveform = analysis.nodes[output_node]
        self.time_trace = analysis.time
        if show:
            plt.plot(analysis.nodes['node0'], label = 'In')
            plt.plot(analysis.nodes[output_node], label = 'Out')
            plt.legend()
            plt.show()
    def extract_data(self):
        '''
        extract the node features and path features and labels
        return:
        1 node features : [#nodes, #node features]
        2 path features : [#path features]
        3 labels : [2]
        '''
        # node features : check the first 7 node features of paper. The final one is the order of this node
        num_nodes = self.num_stages + 1
        node_features = np.zeros(shape=(num_nodes, 9))
        for i_node in range(num_nodes):
            cap_value = 0 if i_node==0 else self.Cs[i_node-1]
            num_i_nodes = 0 if i_node==0 else 1
            num_o_nodes = 1 if (i_node==num_nodes-1 or i_node==0) else 2
            tot_i_cap = np.sum(self.Cs[0:i_node])
            tot_o_cap = np.sum(self.Cs) - tot_i_cap
            num_conn_res = 1 if (i_node==0 or i_node==num_nodes-1) else 2
            tot_i_res = np.sum(self.Rs[0:i_node])
            tot_o_res = np.sum(self.Rs) - tot_i_res
            node_features[i_node,:] = np.array([
                cap_value, num_i_nodes, num_o_nodes, tot_i_cap, tot_o_cap,
                num_conn_res, tot_i_res, tot_o_res, i_node
            ])
        # path features
        path_features = np.array([self.in_slew, self.Cs[-1]])
        # labels
        delay, slew = get_delay_slew(in_wave=self.in_waveform, out_wave=self.out_waveform, time_wave=self.time_trace)
        return node_features, path_features, delay, slew


