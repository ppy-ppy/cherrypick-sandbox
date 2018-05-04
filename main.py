from sandbox import job_classifier,config_selection, find_cluster, update_bo


# Phase 1: Create the experiment (if new), start BO, and return the next sample/current best configuration.
def softmax_application_classifier(input_data):
    (io_weight, cpu_weight), job_class = job_classifier.softmax_classifier(input_data)
    return (io_weight, cpu_weight), job_class


# Phase 2: Create the experiment (if new), start BO, and return the next sample/current best configuration.
def select_configuration(user_id, job_id, data_size, timestamp, is_to_optimize=True):
    exp_name, vm, vcpus, ram, disk, cluster_size = \
        config_selection.select_configuration(user_id, job_id, data_size, timestamp, is_to_optimize)

    return exp_name, vm, vcpus, ram, disk, cluster_size


# Phase 3: Check if the cluster under selected configuration exists. If not, create it.
def check_or_create_cluster(vm, cluster_size):
    ip_address = find_cluster.check_or_create_cluster(vm, cluster_size)
    return ip_address


# Phase 4: Receive the running time and update BO
def find_and_update_run(vm, cluster_size, exp_name, time, scale):
    run = update_bo.find_and_update_run(vm, cluster_size, exp_name, time, scale)
    return run


if __name__ == '__main__':
    # exp_name, vm, vcpus, ram, disk, cluster_size = select_configuration("user9", "job", "1", "20180428", True)
    # print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    # print exp_name, vm, vcpus, ram, disk, cluster_size

    # check_or_create_cluster(vm, cluster_size)
    # print "cluster"
    # master_ip = check_or_create_cluster("c3.large", "8")
    # if not master_ip:
    #     print "The cluster is starting..."
    # else:
    #     print "Master IP: ", master_ip

    # find_and_update_run("c3.xlarge", "2", "terasort", "50")
    print softmax_application_classifier([1, 3, 1, 1, 0])
