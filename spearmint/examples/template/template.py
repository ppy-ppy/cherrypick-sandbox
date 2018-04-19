from schema import *
from experiment_config import *
import math
from path_config_1 import *
import time
import random


def vm_name(vm_type, vm_size):
    vm_type = vm_type[0]
    vm_size = vm_size[0]

    prefix = vm_type
    suffix = vm_size

    if suffix == "small" and prefix != "r2":
        raise Exception("Invalid Machine Type!")

    return ".".join([prefix, suffix])


def is_valid_cluster_size(cluster_size):
    if cluster_size == 2 or cluster_size == 4 or cluster_size == 8 or cluster_size == 16:
        return True
    return False


def get_cost(spec):
    vm_type = spec['vm_type']
    vm_size = spec['vm_size']
    cluster_size = spec['machine_count']
    total_cost = 0.0
    print vm_type, vm_size, cluster_size
    if not is_valid_cluster_size(int(cluster_size)):
        raise Exception("Invalid Machine Count!")

    vm = vm_name(vm_type, vm_size)

    vm_0 = VirtualMachineType.selectBy(name=vm).getOne()

    try:
        config = Configuration.selectBy(vm=vm_0, count=int(cluster_size)).getOne()
    except:
        Configuration(vm=vm_0, count=int(cluster_size))
        config = Configuration.selectBy(vm=vm_0, count=int(cluster_size)).getOne()

    # benchmark meta jobs
    # for i in range(5):
    #     if WEIGHT[i] == 0:
    #         continue
    #
    #     exp = Experiment.find(EXPERIMENT[i])
    #     print EXPERIMENT[i]
    #
    #     data = vm + " " + str(cluster_size[0]) + " " + EXPERIMENT[i]
    #     file_path = os.path.join(EXP_PATH, EXP_TYPE, "experiment.txt")
    #     print file_path
    #     file_object = open(file_path, 'w')
    #     file_object.write(data)
    #     file_object.close()
    #
    #     print "experiment: ", exp
    #     runs = exp.find_runs(vm, int(cluster_size))
    #     print "runs: ", runs
    #
    #     if not runs:
    #         num = 0
    #         run_time = 0
    #         Run(exp=exp, config=config, time=run_time, num=num)
    #         runs = exp.find_runs(vm, int(cluster_size))
    #
    #     for j in range(WEIGHT[i]):
    #         while runs[0].num != 1:
    #             time.sleep(5)
    #             runs = exp.find_runs(vm, int(cluster_size))
    #             print runs[0]
    #
    #         runs[0].num = 0
    #
    #         if TIME_LIMIT != -1 and runs[0].time > TIME_LIMIT:
    #             raise Exception("Run Time Exceeds!")
    #         total_cost += math.log(runs[0].cost) * runs[0].time

    # single experiment as a whole
    exp = Experiment.find(EXP_TYPE)

    data = vm + " " + str(cluster_size[0]) + " " + EXP_TYPE
    file_path = os.path.join(EXP_PATH, EXP_TYPE, "experiment.txt")
    print file_path
    file_object = open(file_path, 'w')
    file_object.write(data)
    file_object.close()

    print "experiment: ", exp
    runs = exp.find_runs(vm, int(cluster_size))
    print "runs: ", runs

    if not runs:
        num = 0
        run_time = 0
        Run(exp=exp, config=config, time=run_time, num=num)
        runs = exp.find_runs(vm, int(cluster_size))

    while runs[0].num != 1:
        time.sleep(5)
        runs = exp.find_runs(vm, int(cluster_size))
        print runs[0]

    runs[0].num = 0

    if TIME_LIMIT != -1 and runs[0].time > TIME_LIMIT:
        raise Exception("Run Time Exceeds!")
    total_cost += math.log(runs[0].cost) * runs[0].time

    print "total cost: ", total_cost
    exp_type = Experiment.find(EXP_TYPE)
    if exp_type.count > 0:
        exp_type.count -= 1
    return total_cost


def main(job_id, params):
    return COST_FUNC(get_cost(params))
