import random
from schema import *
from cherrypick_config import *
import sys


def find_and_update_run(vm, cluster_size):
    exp = Experiment.find(EXPERIMENT)

    runs = exp.find_runs(vm, int(cluster_size))
    run_time = run_and_log(vm, cluster_size)
    runs[0].time = runs[0].time * GAMMA + run_time
    runs[0].num = 0
    exp.count -= 1
    return runs[0]


def run_and_log(vm, cluster_size):
    command = "./run.sh 0 " + EXPERIMENT + " " + vm + " " + cluster_size
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


if __name__ == '__main__':
    print find_and_update_run(*sys.argv[1:3])