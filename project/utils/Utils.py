import numpy as np
from PySpice.Spice.Netlist import Circuit

def get_delay_slew(in_wave, out_wave, time_wave):
    '''
    assume in_wave and out_wave is monotonic
    return delay and slew in 1ns unit
    '''
    in_wave = np.array(in_wave)
    out_wave = np.array(out_wave)
    time_wave_ns = np.array(time_wave * 1e9)
    try:
        # calculate the delay
        input_half_point = np.argwhere(in_wave>=0.5)[0]
        output_half_point = np.argwhere(out_wave>=0.5)[0]
        delay = time_wave_ns[output_half_point] - time_wave_ns[input_half_point]
        # calculate the slew
        output_10p_point = np.argwhere(out_wave>=0.1)[0]
        output_90p_point = np.argwhere(out_wave>=0.9)[0]

        slew = time_wave_ns[output_90p_point] - time_wave_ns[output_10p_point]
        return delay, slew
    except:
        raise Exception("The output waveform has not been settled! Increase your period!")






