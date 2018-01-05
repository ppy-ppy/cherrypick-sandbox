from schema import *
from run_job import run_job


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

    return runs[0]


if __name__ == '__main__':
    file_path = os.path.join(os.path.abspath("../spearmint/examples/typeca/"), "experiment.txt")
    file_object = open(file_path, 'r')
    data = file_object.read()
    vm, cluster_size, exp_name = data.split(' ')
    print vm
    print cluster_size
    print exp_name
    print find_and_update_run(vm, cluster_size, exp_name)

