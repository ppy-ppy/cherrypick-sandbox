import os
from sqlobject import *

from openstack import OPENSTACK_MACHINES


def create_database():
    map(lambda tbl: tbl.createTable(),
        [VirtualMachineType, Configuration, Experiment, Run, BestConfiguration])
    create_virtual_machines()


def setup_connection():
    db_filename = os.path.abspath(os.path.join(__file__, '..', 'data', 'openstackexp.db'))
    connection_string = 'sqlite:' + db_filename
    connection = connectionForURI(connection_string)
    sqlhub.processConnection = connection
    if not os.path.exists(db_filename):
        create_database()


def machine_cost(name):
    return OPENSTACK_MACHINES[name][0]


def machine_ram(name):
    return OPENSTACK_MACHINES[name][1]


def machine_cpu_count(name):
    return OPENSTACK_MACHINES[name][2]


def machine_root_disk(name):
    return OPENSTACK_MACHINES[name][3]


def create_virtual_machines():
    for name in OPENSTACK_MACHINES:
        VirtualMachineType(name=name,
                           ram=machine_ram(name),
                           cpu_count=machine_cpu_count(name),
                           root_disk=machine_root_disk(name),
                           cost=machine_cost(name))


class VirtualMachineType(SQLObject):
    name = StringCol()
    ram = FloatCol()
    cpu_count = IntCol()
    root_disk = FloatCol()
    cost = FloatCol()
    configs = MultipleJoin('Configuration')


class Configuration(SQLObject):
    count = IntCol()
    vm = ForeignKey('VirtualMachineType')
    runs = MultipleJoin('Run')

    @property
    def cost(self):
        return self.vm.cost * self.count

    @property
    def cores(self):
        return self.vm.cpu_count * self.count

    @property
    def vm_size(self):
        return self.vm.name.split(".")[1]

    @property
    def vm_type(self):
        return self.vm.name.split(".")[0]

    @property
    def ram(self):
        return self.vm.ram * self.count

    @property
    def name(self):
        return "%d x %s.%s" % (self.count, self.vm_type, self.vm_size)


class Experiment(SQLObject):
    name = StringCol()
    runs = MultipleJoin('Run', joinColumn='exp_id')

    def find_runs(self, vm_name, count):
        vm = VirtualMachineType.selectBy(name=vm_name).getOne()
        config = Configuration.selectBy(vm=vm, count=count).getOne()
        return list(Run.selectBy(exp=self, config=config))

    @classmethod
    def find(kls, name):
        return kls.selectBy(name=name).getOne()


class Run(SQLObject):
    exp = ForeignKey('Experiment')
    config = ForeignKey('Configuration')
    time = FloatCol()
    num = IntCol()

    @property
    def cost(self):
        return self.config.cost * self.time


class BestConfiguration(SQLObject):
    exp = ForeignKey('Experiment')
    config = ForeignKey('Configuration')
    cost = FloatCol()

setup_connection()
