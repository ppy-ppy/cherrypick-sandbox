from sandbox import config_selection, job_analysis, db_operator


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


def insert_job(job_name, user_id, cpu_percentage, io_percentage):
    db_operator.insert_job_info(job_name, user_id, cpu_percentage, io_percentage)


def insert_runtime(job_id, data_size, vm_name, vm_count, run_time):
    db_operator.insert_run_time(job_id, data_size, vm_name, vm_count, run_time)


def insert_best_configuration(job_name, user_id, vm_name, vm_count, data_size, cost):
    db_operator.insert_best_configuration(job_name, user_id, vm_name, vm_count, data_size, cost)


if __name__ == '__main__':
    job_id = "terasort"
    data_size = 1
    user_id = "weight22"
    timestamp = "20180511"

    exp_name, vm, vcpus, ram, disk, cluster_size = \
        select_configuration(user_id, job_id, str(data_size), timestamp, False)
