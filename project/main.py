import multiprocessing

from utils.SingleTransmissionLine import SingleTransmissionLine_Generator
import numpy as np
import os



def gen_data(NUM_PATHS, NUM_STAGES, pulse_period):
    proc_id = os.getpid()
    data_node_features = np.empty(shape=(NUM_PATHS, NUM_STAGES + 1, 9))
    data_path_features = np.empty(shape=(NUM_PATHS, 2))
    data_label_slew = np.empty(shape=(NUM_PATHS))
    data_label_delay = np.empty(shape=(NUM_PATHS))
    for i in range(NUM_PATHS):
        rise_time = np.random.randint(low=10, high=100)
        C = np.random.randint(low=1, high=10, size=NUM_STAGES)
        R = np.random.randint(low=1, high=10, size=NUM_STAGES)

        circuit_obj = SingleTransmissionLine_Generator('RC Line', NUM_STAGES, R, C)
        circuit_obj.build()
        circuit_obj.simulate(rise_time=rise_time, pulse_period=pulse_period, precision=10, show=False)
        node_features, path_features, delay, slew = circuit_obj.extract_data()

        data_node_features[i,:,:] = node_features
        data_path_features[i,:] = path_features
        data_label_slew[i] = slew
        data_label_delay[i] = delay
        if i%100 == 0:
            print(f'PID:{proc_id}, Generated paths: {i}')
    return (data_node_features, data_path_features, data_label_slew, data_label_delay)

if __name__ == "__main__":
    # specify num. of processes
    NUM_CORES = 8
    # num. of paths in dataset
    NUM_PATHS = 2000
    # num. of stages for the circuit, this can also be put into the loop and be a random variable
    NUM_STAGES = 8
    # num. of steps in a period, each step is 1ns
    pulse_period = 10000

    paths_per_process = NUM_PATHS//NUM_CORES

    data_node_features = np.empty(shape=(NUM_PATHS, NUM_STAGES + 1, 9))
    data_path_features = np.empty(shape=(NUM_PATHS, 2))
    data_label_slew = np.empty(shape=(NUM_PATHS))
    data_label_delay = np.empty(shape=(NUM_PATHS))

    # pool = multiprocessing.Pool(processes=NUM_CORES)
    # results = []
    # for i in range(NUM_CORES):
        # results.append(pool.apply_async(gen_data, (paths_per_process, NUM_STAGES, pulse_period)))
    # pool.close()
    # pool.join()

    results = gen_data(NUM_PATHS, NUM_STAGES, pulse_period)

    data_node_features, data_path_features, data_label_slew, data_label_delay = results

    np.save('data_node_features.npy', data_node_features)
    np.save('data_path_features.npy', data_path_features)
    np.save('data_label_slew.npy', data_label_slew)
    np.save('data_label_delay.npy', data_label_delay)

    # for i, res in enumerate(results):
    #     print(type(res.get()))
    #     data_node_features[i*paths_per_process:(i+1)*paths_per_process, :, :] = res.get()[0]
    #     data_path_features[i * paths_per_process:(i + 1) * paths_per_process, :] = res.get()[1]
    #     data_label_slew[i * paths_per_process:(i + 1) * paths_per_process] = res.get()[2]
    #     data_label_delay[i * paths_per_process:(i + 1) * paths_per_process] = res.get()[3]
    # np.save('data_node_features.npy', data_node_features)
    # np.save('data_path_features.npy', data_path_features)
    # np.save('data_label_slew.npy', data_label_slew)
    # np.save('data_label_delay.npy', data_label_delay)