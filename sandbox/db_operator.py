import math
from spearmint.schema import *
import experiment


def insert_job_info(job_id, user_id, cpu_percentage, io_percentage):
    JobInfo(name=job_id,
            user_id=user_id,
            cpu_percentage=cpu_percentage,
            io_percentage=io_percentage)


def insert_run_time(job_id, data_size, vm_name, vm_count, run_time):
    vm = VirtualMachineType.selectBy(name=vm_name).getOne()
    vm_id = vm.id
    config = Configuration.selectBy(id=vm_id, count=vm_count).getOne()
    config_id = config.id
    Runtime(job=job_id,
            data_size=data_size,
            config=config_id,
            run_time=run_time)


def insert_best_configuration(exp, config, cost):
    job_id = JobInfo.selectBy(name=exp.job_id, user_id=exp.user_id).getOne().id
    vm_id = VirtualMachineType.selectBy(name=config.vm.name).getOne().id
    config_id = Configuration.selectBy(count=config.machine_count, vm=vm_id).getOne().id

    try:
        best_config = BestConfiguration.selectBy(job=job_id).getOne()
        best_config.data_size = float(exp.data_group)
        best_config.config_id = config_id
        best_config.cost = cost

    except SQLObjectNotFound:
        BestConfiguration(job=job_id, data_size=float(exp.data_group), config=config_id, cost=cost)


def add_flavor(vm_name, vcpu, ram, disk, cost):
    vm = experiment.VirtualMachine(vm_name, vcpu, ram, disk)
    vm.insert_vm(cost)


def get_run_cost(exp, config):
    job = JobInfo.find_job_info(exp.job_id, exp.user_id)
    runs = job.find_runs(config.vm.name, config.machine_count, float(exp.data_group))
    total_cost = math.log(runs[0].cost) * runs[0].run_time
    return math.log(total_cost)


if __name__ == '__main__':
    add_flavor('m1.2xlarge', 16, 32, 320, 0)
