import math

import job_analysis
from spearmint.schema import VirtualMachineType as VM
from spearmint.schema import Configuration as Config


class VirtualMachine(object):
    # flavor_space = [
    #     "m1.medium",
    #     "m1.large",
    #     "m1.xlarge",
    #     "r2.small",
    #     "r2.medium",
    #     "r2.large",
    #     "r2.xlarge",
    #     "c3.medium",
    #     "c3.large",
    #     "c3.xlarge"
    # ]

    def __init__(self, vm_name, vcpu, ram, disk):
        self.name = vm_name
        self.vcpu = vcpu
        self.ram = ram
        self.disk = disk

    def insert_vm(self, cost):
        VM(name=self.name, ram=self.ram, cpu_count=self.vcpu, root_disk=self.disk, cost=cost)

    def cost(self):
        vm = VM.selectBy(name=self.name).getOne()
        return float(vm.cost)


class Configuration(object):
    # machine_space = [2, 4, 8, 16]

    def __init__(self, machine_count, vm_name, vcpu, ram, disk):
        self.machine_count = machine_count
        self.vm = VirtualMachine(vm_name, vcpu, ram, disk)

    # def check_valid_cluster_size(self):
    #     if self.machine_count not in Configuration.machine_space:
    #         return False
    #     return True

    def insert_config(self):
        vm_0 = VM.selectBy(name=self.vm.name).getOne()
        Config(vm=vm_0, count=self.machine_count)

    def get_config(self):
        vm_0 = VM.selectBy(name=self.vm.name).getOne()
        try:
            config = Config.selectBy(vm=vm_0, count=self.machine_count).getOne()
        except:
            self.insert_config()
            config = Config.selectBy(vm=vm_0, count=self.machine_count).getOne()
        return config

    @property
    def cost(self):
        vm_cost = self.vm.cost
        cost = vm_cost * self.machine_count
        return math.log(cost)


class Experiment(object):
    data_split = [0, 1, 5, 10, 100]

    def __init__(self, job_id, user_id, data_size, io_percentage=None, cpu_percentage=None, best_configuration=None):

        self.job_id = job_id
        self.user_id = user_id
        self.data_size = data_size
        self.io_percentage = io_percentage
        self.cpu_percentage = cpu_percentage
        self.best_configuration = best_configuration

    def set_io_cpu_percentage(self):
        io_weight, cpu_weight = job_analysis.get_io_cpu_analysis(self.job_id)
        self.io_percentage = float(io_weight)
        self.cpu_percentage = float(cpu_weight)

    def set_best_configuration(self,  machine_count, vm_name, vcpu, ram, disk):
        self.best_configuration = Configuration(machine_count, vm_name, vcpu, ram, disk)

    @property
    def data_group(self):
        data_group = "0"
        for split in Experiment.data_split:
            if self.data_size - split < 0:
                break
            data_group = str(split)
        return data_group

    @property
    def name(self):
        name = str(self.user_id) + "-" + str(self.job_id) + "-" + str(self.data_group)
        return name

