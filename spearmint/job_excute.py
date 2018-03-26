from softmax_classifier import softmax_classifier
from runtest import *
from path_config import *
import os
import multiprocessing
import time
from schema import Experiment as Exp
import subprocess
# from spearmint.main import *
import signal


# job_id_to_weight_dict = {"abc": [1, 3, 1, 1, 0]}
#
#
# def job_id_to_weight(job_id):
#     return job_id_to_weight_dict[job_id]


# def job_io_cpu_feature(job_id, data_size):
#     flag = True
#     exp_name = job_id + "-" + data_size
#     new_path = os.path.join(EXP_PATH, exp_name)
#     if not os.path.exists(new_path):
#         flag = False
#         old_path = os.path.join(EXP_PATH, 'template')
#         copy_tree(old_path, new_path)
#         rename_exp(new_path, exp_name)
#         replace_exp(old_path, new_path, "config.pb", exp_name)
#         replace_exp(old_path, new_path, "experiment_config.py", exp_name)
#
#     job_weight = job_id_to_weight(job_id)
#     a, b = softmax_classifier(job_weight)
#     if not flag:
#         write_file = open(os.path.join(new_path, "experiment_config.py"), "r+")
#         write_file.seek(0, 2)
#         write_file.write("WEIGHT = " + str(job_weight))
#         write_file.close()
#         flag = True
#
#     # vm
#
#     base_dir = os.path.abspath(os.path.dirname(__file__))
#     print base_dir
#     if not os.path.exists(base_dir+"/examples/"+exp_name+"/experiment.txt"):
#         command_ = "python " + base_dir + "/spearmint/main.py  " + base_dir + "/examples/" + exp_name + "/config.pb"
#         p = multiprocessing.Process(name="BO_process", target=os.system, args=(command_,))
#         p.start()
#
#     while not os.path.exists(base_dir+"/examples/"+exp_name+"/experiment.txt"):
#         pass
#
#     read_file = base_dir+"/examples/"+exp_name+"/experiment.txt"
#     file_object = open(read_file, 'r')
#     data = file_object.read()
#     vm, cluster_size, exp_name = data.split(' ')
#     return a, b, vm, int(cluster_size)  # a=(io_percentage,cpu_percentage)


# def job_excute(job_id, data_size):
#     exp_name = job_id + "-" + data_size
#     base_dir = os.path.abspath(os.path.dirname(__file__))
#     command_ = "python " + base_dir + "/examples/" + exp_name + "/offline.py"
#     os.system(command_)
#
#     while not os.path.exists(base_dir+"/examples/"+exp_name+"/total_time.txt"):
#         pass
#
#     read_file = open(base_dir+"/examples/"+exp_name+"/total_time.txt", "r")
#     total_time = float(read_file.read())
#     print(total_time)
#     os.system("rm -f "+base_dir+"/examples/"+exp_name+"/total_time.txt")
#     return total_time

###############################################################################################################
# Phase 1: Create the experiment (if new), start BO, and return the next sample/current best configuration.
###############################################################################################################


def create_experiment(exp_name, exp_path):
    copy_tree(TEMPLATE_PATH, exp_path)
    rename_exp(exp_path, exp_name)
    replace_exp(TEMPLATE_PATH, exp_path, "config.pb", exp_name)
    replace_exp(TEMPLATE_PATH, exp_path, "experiment_config.py", exp_name)

    # write the new experiment into DB
    try:
        new_experiment = Exp(name=exp_name, count=0)
    except Exception, e:
        print e


def start_bo(exp_name):
    config_path = os.path.join(EXP_PATH, exp_name, "config.pb")
    command_ = "python " + MAIN_PATH + " " + config_path
    print command_

    process_list = os.popen("ps a").read()
    print type(process_list)
    print process_list
    if command_ not in process_list:
        p = multiprocessing.Process(name="BO_process", target=os.system, args=(command_,))
        print "Starting BO..."
        p.start()
        print p.pid
        print p.name


def get_best_config(exp_name, is_to_optimize):
    if is_to_optimize:
        file_name = "experiment.txt"
    else:
        file_name = "best_job_and_result.txt"

    file_path = os.path.join(EXP_PATH, exp_name, file_name)

    while not os.path.exists(file_path):
        pass

    file_object = open(file_path, 'r')
    data = file_object.read()

    if is_to_optimize:
        vm, cluster_size, exp = data.split(' ')
    else:
        data = data.split("Parameters: \n")
        lines = data[1].split("\n")
        data = ""
        for line in lines:
            line = line.replace("name: ", '')
            line = line.replace("str_val: ", '')
            line = line.replace("int_val: ", '')
            line = line.replace('"', '')
            line = line.replace("\n", "")
            line = line.replace("vm_type", "")
            line = line.replace("vm_size", ".")
            line = line.replace("machine_count", ", ")
            data += line

        vm, cluster_size = data.split(", ")
    return vm, int(cluster_size)


def select_configuration(user_id, job_id, data_size, is_to_optimize):
    exp_name = user_id + "-" + job_id + "-" + data_size
    exp_path = os.path.join(EXP_PATH, exp_name)
    if not os.path.exists(exp_path):
        create_experiment(exp_name, exp_path)
    start_bo(exp_name)
    vm, cluster_size = get_best_config(exp_name, is_to_optimize)
    exp = Exp.find(exp_name)

    return exp_name, vm, cluster_size


###############################################################################################################
# Phase 2: Check if the cluster under selected configuration exists. If not, create it.
###############################################################################################################


def check_or_create_cluster(vm, cluster_size):
    # TODO: check if the cluster exists

    command = EXE_PATH + "/setup.sh 0 terasort " + vm + " " + str(cluster_size)
    print os.system(command)


if __name__ == '__main__':
    exp_name, vm, cluster_size = select_configuration("user1", "job", "2", True)
    print exp_name, vm, cluster_size
    # check_or_create_cluster(vm, cluster_size)
    # print "cluster"



