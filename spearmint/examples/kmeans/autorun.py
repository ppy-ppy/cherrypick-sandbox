import random
from schema import *
from cherrypick_config import *
import sys


def find_and_update_run(vm, cluster_size):
    exp = Experiment.find(EXPERIMENT)
    runs = exp.find_runs(vm, int(cluster_size))
    runs[0].num = 0
    return runs[0]


if __name__ == '__main__':
    print find_and_update_run(*sys.argv[1:3])

