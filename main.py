from sandbox import config_selection, job_analysis, db_operator
from sandbox.experiment import *
from ernest.main import ddl_based_best_configuration


def select_configuration(user_id, job_id, data_size, deadline=None, is_to_optimize=True):

    experiment = Experiment(job_id, user_id, data_size)
    experiment.set_io_cpu_percentage()

    if deadline:
        best_configuration, lowest_cost = config_selection.select_configuration_with_ddl(experiment, deadline)
        if not best_configuration:
            print "======================================================"
            print "No available configuration!"
            return experiment.name, None, None, None, None, None
    else:
        best_configuration = config_selection.select_configuration(experiment, is_to_optimize)
        lowest_cost = config_selection.get_lowest_cost(experiment)
        db_operator.insert_best_configuration(experiment, best_configuration, lowest_cost)

    if not is_to_optimize:
        print "======================================================"
        print "Job ID: ", experiment.job_id
        print "User ID: ", experiment.user_id
        print "Data Size (G): ", experiment.data_group
        print "Best Configuration: "
        print "\tVCPU(s): ", best_configuration.vm.vcpu
        print "\tRAM (G): ", best_configuration.vm.ram
        print "\tDISK (G): ", best_configuration.vm.disk
        print "\tSIZE: ", best_configuration.machine_count
        print "Recommended Configuration: ", best_configuration.vm.name, "*", best_configuration.machine_count
        print "Cost: ", lowest_cost

    return experiment.name, best_configuration.vm.name, best_configuration.machine_count, \
           best_configuration.vm.vcpu, best_configuration.vm.ram, best_configuration.vm.disk


if __name__ == '__main__':
    job_id = "terasort"
    data_size = 1
    user_id = "user9"
    deadline = 40

    exp_name, vm, vcpus, ram, disk, cluster_size = \
        select_configuration(user_id, job_id, data_size, deadline, False)
