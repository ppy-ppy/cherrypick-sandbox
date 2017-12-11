import os
import time
import random
from schema import *
from cherrypick_config import *


def vm_name(vm_type, vm_size):
    vm_type = vm_type[0]
    vm_size = vm_size[0]

    prefix = vm_type
    suffix = vm_size

    return ".".join([prefix, suffix])


def run_job(vm, cluster_size):
    command = "./run.sh 0 " + EXPERIMENT + " " + vm + " " + str(cluster_size)
    print os.system(command)

    dirname = EXPERIMENT + '-' + vm + '-' + str(cluster_size) + "-results"  # 'local_type' will be replaced by vm in the future.

    while os.path.exists(dirname) is False:
        continue
    filename = dirname + '/1/' + vm + '.time'  # 'local_type' will be replaced by vm in the future.
    f = open(filename)
    line = f.readline()
    run_time = float(line.split(',')[1])

    vm_size = vm.split('.')[1]
    if vm_size == 'nano':
        run_time = random.uniform(32, 64)
    elif vm_size == 'micro':
        run_time = random.uniform(16, 32)
    elif vm_size == 'tiny':
        run_time = random.uniform(8, 16)
    elif vm_size == 'small':
        run_time = random.uniform(4, 8)
    elif vm_size == 'large':
        run_time = random.uniform(2, 4)
    elif vm_size == 'xlarge':
        run_time = random.uniform(1, 2)

    print "run time is :", run_time
    return run_time


def find_runs(spec):
    vm_type = spec['vm_type']
    vm_size = spec['vm_size']
    cluster_size = spec['machine_count']
    print vm_type, vm_size, cluster_size

    vm = vm_name(vm_type, vm_size)
    exp = Experiment.find(EXPERIMENT)
    vm_0 = VirtualMachineType.selectBy(name=vm).getOne()

    try:
        config = Configuration.selectBy(vm=vm_0, count=int(cluster_size)).getOne()
    except:
        Configuration(vm=vm_0, count=int(cluster_size))
        config = Configuration.selectBy(vm=vm_0, count=int(cluster_size)).getOne()

    runs = exp.find_runs(vm, int(cluster_size))
    print "runs", runs

    if runs:
        print vm, cluster_size
        while runs[0].num != 0:
            time.sleep(5)
            runs = exp.find_runs(vm, int(cluster_size))
            print runs[0]

        runs[0].num = 1

    else:
        num = 1
        run_time = run_job(vm, cluster_size[0])

        Run(exp=exp, config=config, time=run_time, num=num)

    runs = exp.find_runs(vm, int(cluster_size))
    print "[@]> %s\t%s\t%d\t%.2f\t%.4f\t%.4f" % \
          (exp.name, vm, int(cluster_size), runs[0].time, runs[0].cost, COST_FUNC(runs[0]))

    if TIME_LIMIT != -1 and runs[0].time > TIME_LIMIT:
        raise Exception("Run Time Exceeds!")

    return runs[0]


def main(job_id, params):
    return COST_FUNC(find_runs(params))
