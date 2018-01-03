
from schema import *
from experiment_config import *
from run_job import run_job


def find_and_update_run(vm, cluster_size, exp_name):
    exp = Experiment.find(exp_name)

    runs = exp.find_runs(vm, int(cluster_size))
    run_time = run_job(vm, cluster_size, exp_name)
    runs[0].time = runs[0].time * GAMMA + run_time
    # runs[0].time = 1
    runs[0].num = 1
    return runs[0]


if __name__ == '__main__':
    file_path = os.path.join(os.path.abspath("../spearmint/examples/typeda/"), "experiment.txt")
    file_object = open(file_path, 'r')
    data = file_object.read()
    vm, cluster_size, exp_name = data.split(' ')
    print vm
    print cluster_size
    print exp_name
    print find_and_update_run(vm, cluster_size, exp_name)
