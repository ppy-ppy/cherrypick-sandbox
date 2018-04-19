from schema import *
from experiment_config import *
from run_job import run_job
from path_config_1 import *
import time


def find_and_update_run(vm, cluster_size, exp_name):
    exp = Experiment.find(exp_name)

    vm_0 = VirtualMachineType.selectBy(name=vm).getOne()
    try:
        config = Configuration.selectBy(vm=vm_0, count=int(cluster_size)).getOne()
    except:
        Configuration(vm=vm_0, count=int(cluster_size))
        config = Configuration.selectBy(vm=vm_0, count=int(cluster_size)).getOne()

    runs = exp.find_runs(vm, int(cluster_size))
    if not runs:
        num = 0
        run_time = 0
        Run(exp=exp, config=config, time=run_time, num=num)
        runs = exp.find_runs(vm, int(cluster_size))

    if runs[0].time != 0:
        runs[0].num = 1
    else:
        run_time = run_job(vm, cluster_size, exp_name)
        if run_time != -1:
            runs[0].time = run_time
            # runs[0].time = 1
            runs[0].num = 1

        runs = exp.find_runs(vm, int(cluster_size))
        print runs[0]

    return runs[0].time


def total_job_time():
    file_path = os.path.join(EXP_PATH, EXP_TYPE, "experiment.txt")

    sub_job_num = sum(WEIGHT)
    total_time = 0
    for i in range(sub_job_num):
        file_object = open(file_path, 'r')
        data = file_object.read()
        file_object.close()

        vm, cluster_size, exp_name = data.split(' ')
        temp=find_and_update_run(vm, cluster_size, exp_name)
        time.sleep(5)
        print(exp_name,temp)
        total_time+=temp

    temp_dir=os.path.abspath(os.path.dirname(__file__))
    temp_dir+="/total_time.txt"
    write_file=open(temp_dir,'w+')
    write_file.write(str(total_time))
    write_file.close()


if __name__ == '__main__':
    # file_path = os.path.join(EXP_PATH, EXP_TYPE, "experiment.txt")
    # file_object = open(file_path, 'r')
    # data = file_object.read()
    # vm, cluster_size, exp_name = data.split(' ')
    # print vm
    # print cluster_size
    # print exp_name
    # print find_and_update_run(vm, cluster_size, exp_name)
    total_job_time()

