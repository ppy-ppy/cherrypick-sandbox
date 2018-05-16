from spearmint.schema import *
from experiment_config import *
# from run_job import run_job


def find_and_update_run(vm, cluster_size):
    job = JobInfo.find_job_info(EXP_TYPE, USER)
    runs = job.find_runs(vm, int(cluster_size), float(DATA_GROUP))

    run_time = -1
    # run_time = run_job(vm, cluster_size, exp_name)
    if run_time != -1:
        # runs[0].time = runs[0].time * GAMMA + (1 - GAMMA) * run_time
        runs[0].run_time = run_time
        runs[0].num = 1

    return runs[0]


if __name__ == '__main__':
    exp_name = USER + "-" + EXP_TYPE + "-" + DATA_GROUP
    file_path = os.path.join(EXP_PATH, exp_name, "experiment.txt")
    file_object = open(file_path, 'r')
    data = file_object.read()
    vm, vcpus, ram, disk, cluster_size, exp_name = data.split(' ')
    print vm
    print vcpus, ram, disk
    print cluster_size
    print exp_name
    print find_and_update_run(vm, cluster_size)
