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


def insert_best_configuration(job_name, user_id, vm_name, vm_count, data_size, cost):
    vm_id = VirtualMachineType.selectBy(name=vm_name).getOne().id
    job_id = JobInfo.selectBy(name=job_name, user_id=user_id).getOne().id
    config_id = Configuration.selectBy(count=vm_count, vm=vm_id).getOne().id
    BestConfiguration(job=job_id, data_size=data_size, config=config_id, cost=cost)


def add_flavor(vm_name, vcpu, ram, disk, cost):
    vm = experiment.VirtualMachine(vm_name, vcpu, ram, disk)
    vm.insert_vm(cost)


if __name__ == '__main__':
    add_flavor('m1.2xlarge', 16, 32, 320, 0)
