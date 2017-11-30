import math

from cherrypick_config import *
from schema import *

import os


def vm_name(cpu_count, root_disk):
    cpu_count = cpu_count[0]
    root_disk = root_disk[0]

    prefix = 'm1'
    suffix = None
    if cpu_count == '1' and root_disk == '2':
        suffix = 'nano'
    if cpu_count == '1' and root_disk == '5':
        suffix = 'micro'
    if cpu_count == '1' and root_disk == '10':
        suffix = 'tiny'
    if cpu_count == '1' and root_disk == '20':
        suffix = 'small'
    if cpu_count == '2' and root_disk == '40':
        suffix = 'medium'
    if cpu_count == '4' and root_disk == '80':
        suffix = 'large'
    if cpu_count == '8' and root_disk == '160':
        suffix = 'xlarge'
    if suffix is None:
        raise Exception("Invalid VM type.")

    return ".".join([prefix, suffix])


def find_runs(spec):
    cpu_count = spec['cpu_count']
    root_disk = spec['root_disk']
    cluster_size = spec['machine_count']
    print cpu_count, root_disk, cluster_size

    vm = vm_name(cpu_count, root_disk)
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
        print "[@]> %s\t%s\t%d\t%.2f\t%.4f\t%.4f" % \
              (exp.name, vm, int(cluster_size), runs[0].time, runs[0].cost, COST_FUNC(runs[0]))

    else:
        command = "./run.sh 0 " + EXPERIMENT + " " + vm + " 1"
        print os.system(command)

        dirname = EXPERIMENT + '-' + 'local_type' + '-' + '1' + "-results"  # 'local_type' will be replaced by vm in the future.

        while os.path.exists(dirname) is False:
            continue
        filename = dirname + '/1/' + 'local_type' + '.time'  # 'local_type' will be replaced by vm in the future.
        f = open(filename)
        line = f.readline()
        run_time = float(line.split(',')[1])
        print "run time is :", run_time
        num = 1
        Run(exp=exp, config=config, time=run_time, num=num)

        runs = exp.find_runs(vm, int(cluster_size))
        print "[@]> %s\t%s\t%d\t%.2f\t%.4f\t%.4f" % \
              (exp.name, vm, int(cluster_size), runs[0].time, runs[0].cost, COST_FUNC(runs[0]))

    if TIME_LIMIT != -1 and runs[0].time > TIME_LIMIT:
        raise Exception("Run Time Exceeds!")

    return runs[0]


def main(job_id, params):
    return COST_FUNC(find_runs(params))
