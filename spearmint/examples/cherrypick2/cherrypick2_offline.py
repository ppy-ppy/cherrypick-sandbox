import math

from cherrypick_config import *
from schema import *
import commands

import os

def vm_name(vm_type, cpu_count):
    vm_type = vm_type[0]
    cpu_count = int(cpu_count[0])

    prefix = None
    print vm_type, cpu_count
    if vm_type == 'm4':
        prefix = 'm4'
    if vm_type == 'r3':
        prefix = 'r3'
    if vm_type == 'c4':
        prefix = 'c4'
    if vm_type == 'i2':
        prefix = 'i2'
    if prefix is None:
        raise Exception("Invalid VM type.")

    suffix=None
    if cpu_count == 2:
        suffix = 'large'
    elif cpu_count == 4:
        suffix = 'xlarge'
    elif cpu_count == 8:
        suffix = '2xlarge'
    if suffix is None:
        raise Exception("Invalid VM size.")
    return ".".join([prefix, suffix])

def cluster_size_normalized(name, size):
    vm_size = {'large': 4, 'xlarge': 2, '2xlarge': 1}[name.split(".")[1]]
    return vm_size * 2 * size

def find_runs(spec):
    vm_type = spec['vm_type']
    cpu_count = spec['cpu_count']
    cluster_size = spec['machine_count']
    vm = vm_name(vm_type, cpu_count)
    exp = Experiment.find(EXPERIMENT)
    print EXPERIMENT

    print "exp: ",exp

    vm_0 = VirtualMachineType.selectBy(name=vm).getOne()
    machine = Machine.selectBy(vm=vm_0).getOne()
    config = Configuration.selectBy(machine=machine, count=cluster_size_normalized(vm, int(cluster_size))).getOne()

    runs = exp.find_runs(vm, cluster_size_normalized(vm, int(cluster_size)))
    print "runs", runs
    if runs:
        print "[@]> %s\t%s\t%d\t%.2f\t%.4f\t%.4f" % (exp.name, vm, int(cluster_size), runs[0].time, runs[0].cost, COST_FUNC(runs[0]))

    else:

        print "run"
        command = "./run.sh 0 " + EXPERIMENT + " " + vm + " 1"
        print os.system(command)

        dirname = EXPERIMENT + '-' + 'local_type' + "-1-results"  # 'local_type' will be replaced by vm in the future.
        print dirname
        while os.path.exists(dirname) is False:
            continue
        filename = dirname + '/1/' + 'local_type' + '.time' # 'local_type' will be replaced by vm in the future.
        f = open(filename)
        line = f.readline()
        run_time = float(line.split(',')[1])
        print "run time is :", run_time
        num = 1
        Run(exp=exp, config=config, time=run_time, num=num)

        runs = exp.find_runs(vm, cluster_size_normalized(vm, int(cluster_size)))
        print "[@]> %s\t%s\t%d\t%.2f\t%.4f\t%.4f" % (exp.name, vm, int(cluster_size), runs[0].time, runs[0].cost, COST_FUNC(runs[0]))

    if runs[0].time > TIME_LIMIT:
        raise Exception("Run Time Exceeds!")

    return runs[0]


def main(job_id, params):
    print "params: ", params
    print os.path.abspath('.')
    return COST_FUNC(find_runs(params))
