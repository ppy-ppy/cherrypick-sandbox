from env_config import *
from ernest.output_data import *
from spearmint.schema import Experiment as Exp


def find_and_update_run(vm, cluster_size, exp_name, time, scale):
    exp = Exp.find(exp_name)
    runs = exp.find_runs(vm, int(cluster_size))
    if float(time) != -1:
        runs[0].time = runs[0].time * GAMMA + (1 - GAMMA) * float(time)
        runs[0].num = 1
        # print vm
    # print runs
    output_test_time_ernest(vm, int(cluster_size), exp_name, float(time), str(scale))
    return runs[0]