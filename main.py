from sandbox import config_selection, job_analysis, db_operator
from sandbox.experiment import *


def select_configuration(user_id, job_id, data_size, is_to_optimize=True):

    print user_id, job_id
    experiment = Experiment(job_id, user_id, data_size)
    print experiment.job_id, experiment.user_id
    experiment.set_io_cpu_percentage()

    best_configuration = config_selection.select_configuration(experiment, is_to_optimize)

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

        lowest_cost = db_operator.get_run_cost(experiment, best_configuration)
        db_operator.insert_best_configuration(experiment, best_configuration, lowest_cost)

    return experiment.name, best_configuration.vm.name, best_configuration.machine_count, \
           best_configuration.vm.vcpu, best_configuration.vm.ram, best_configuration.vm.disk


if __name__ == '__main__':
    job_id = "terasort"
    data_size = 1
    user_id = "user"

    exp_name, vm, vcpus, ram, disk, cluster_size = \
        select_configuration(user_id, job_id, data_size, False)
