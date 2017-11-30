from schema import *
from cherrypick_config import *

import glob
import os


def _find_or_create_class(kls, *args, **kwargs):
    objs = list(kls.selectBy(*args, **kwargs))
    if objs:
        return objs[0]
    return kls(*args, **kwargs)


def find_or_create_configuration(vm, count):
    return _find_or_create_class(Configuration, vm=vm, count=count)


def find_or_create_experiment(name):
    return _find_or_create_class(Experiment, name=name)


def find_or_create_run(exp, num, vm, count, time):
    num = int(num)
    count = int(count)
    time = float(time)

    exp = find_or_create_experiment(exp)
    configuration = find_or_create_configuration(vm, count)
    runs = list(Run.selectBy(config=configuration, exp=exp, num=num))

    if runs:
        return
    Run(exp=exp, config=configuration, time=time, num=num)


def load_file(fname):
    with open(fname, 'r') as f:
        for line in f:
            args = line.strip().split("\t")
            print args
            find_or_create_run(*args)


def load_result_directories(directory):
    wildcard_path = os.path.join(os.path.abspath(directory), "*.tsv")
    for fname in glob.glob(wildcard_path):
        load_file(fname)


def find_or_create_best_configuration(exp, cpu_count, root_disk, machine_count, cost):
    print exp
    vm = VirtualMachineType.selectBy(cpu_count=cpu_count, root_disk=root_disk).getOne()
    print vm
    configuration = Configuration.selectBy(vm=vm, count=machine_count).getOne()
    print configuration
    best_configuration = list(BestConfiguration.selectBy(exp=exp, config=configuration))
    if best_configuration:
        print best_configuration
        if best_configuration[0].cost <= cost:
            return
        else:
            best_configuration[0].cost = cost
    BestConfiguration(exp=exp, config=configuration, cost=cost)


def load_best_configurations(exp):
    file_name = 'best_job_and_result.txt'
    file_path = os.path.join(os.path.abspath('.'), file_name)
    print file_path
    flag = ""
    cpu_count = ""
    root_disk = ""
    machine_count = ""
    cost = ""
    with open(file_path, 'r') as f:
        for line in f:
            args = line.strip().split(": ")
            if args[0] == "Best result":
                cost = args[1]
                continue

            elif args[0] == "name":
                flag = args[1][1: -1]
                continue

            if flag == "cpu_count":
                cpu_count = args[1][1: -1]
                flag = ""

            elif flag == "root_disk":
                root_disk = args[1][1: -1]
                flag = ""
            elif flag == "machine_count":
                machine_count = args[1]
                flag = ""

    cpu_count = int(cpu_count)
    root_disk = float(root_disk)
    machine_count = int(machine_count)
    cost = float(cost)

    find_or_create_best_configuration(exp, cpu_count, root_disk, machine_count, cost)

if __name__ == '__main__':
    #load_result_directories(directory="results")
    exp = Experiment.find(EXPERIMENT)
    load_best_configurations(exp)
