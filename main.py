from sandbox import config_selection, job_analysis


def select_configuration(user_id, job_id, data_size, timestamp, is_to_optimize=True):
    io_weight, cpu_weight = job_analysis.get_io_cpu_analysis(job_id)
    print io_weight, cpu_weight

    exp_name, vm, cluster_size, vcpus, ram, disk = config_selection.\
        select_configuration(user_id, job_id, data_size, timestamp, io_weight, cpu_weight, is_to_optimize)

    print "======================================================"
    print "Job ID: ", job_id
    print "User ID: ", user_id
    print "Data Size (G): ", data_size
    print "Best Configuration: "
    print "\tVCPU(s): ", vcpus
    print "\tRAM (G): ", ram
    print "\tDISK (G): ", disk
    print "\tSIZE: ", cluster_size
    print "Recommended Configuration: ", vm, "*", cluster_size

    return exp_name, vm, cluster_size, vcpus, ram, disk


if __name__ == '__main__':
    job_id = "terasort"
    data_size = 1
    user_id = "weight22"
    timestamp = "20180511"

    exp_name, vm, vcpus, ram, disk, cluster_size = \
        select_configuration(user_id, job_id, str(data_size), timestamp, False)
