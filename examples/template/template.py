from spearmint.schema import *
from experiment_config import *
from sandbox import config_selection
from sandbox.experiment import *
import math
import time


def write_file(path, data):
    file_object = open(path, 'w')
    file_object.write(data)
    file_object.close()


def get_cost(spec):
    vcpus = spec['vcpus']
    ram = spec['ram']
    disk = spec['disk']
    cluster_size = spec['machine_count']
    total_cost = 0.0
    print disk
    disk = 10 * int(disk)
    print vcpus, ram, disk, cluster_size

    job = JobInfo.find_job_info(EXP_TYPE, USER)
    vm_name = config_selection.get_vm_name(job.io_percentage, job.cpu_percentage, int(vcpus), int(ram), disk)
    configuration = Configuration(int(cluster_size), vm_name, int(vcpus), int(ram), disk)

    if not configuration.check_valid_cluster_size():
        raise Exception("Invalid Machine Count!")

    experiment = Experiment(EXP_TYPE, USER, float(DATA_GROUP), job.io_percentage, job.cpu_percentage)

    data = vm_name + " " + \
           str(configuration.vm.vcpu) + " " + \
           str(configuration.vm.ram) + " " + \
           str(configuration.vm.disk) + " " + \
           str(configuration.machine_count) + " " + \
           experiment.name

    file_path = os.path.join(EXP_PATH, experiment.name, "experiment.txt")
    write_file(file_path, data)

    print "experiment: ", job
    runs = job.find_runs(vm_name, configuration.machine_count, float(experiment.data_group))
    print runs

    if not runs:
        num = 0
        run_time = 0
        config = configuration.get_config()
        Runtime(job=job,
                data_size=float(experiment.data_group),
                config=config,
                run_time=run_time,
                num=num)

        runs = job.find_runs(vm_name, configuration.machine_count, float(experiment.data_group))

    while runs[0].num != 1:
        time.sleep(5)
        runs = job.find_runs(vm_name, configuration.machine_count, float(experiment.data_group))
        print runs[0]

    runs[0].num = 0

    if TIME_LIMIT != -1 and runs[0].run_time > TIME_LIMIT:
        raise Exception("Run Time Exceeds!")
    total_cost += math.log(runs[0].cost) * runs[0].run_time

    print "total cost: ", total_cost

    log = vm_name + ", " + \
          str(configuration.machine_count) + ", " + \
          str(configuration.vm.vcpu) + ", " + \
          str(configuration.vm.ram) + ", " + \
          str(configuration.vm.disk) + ", " + \
          str(total_cost) + "\n"

    file_path = os.path.join(EXP_PATH, experiment.name, "log.csv")
    write_file(file_path, log)

    return total_cost


def main(job_id, params):
    return COST_FUNC(get_cost(params))

