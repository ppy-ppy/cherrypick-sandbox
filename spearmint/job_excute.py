from softmax_classifier import softmax_classifier
from runtest import *
from path_config import *
import os
import multiprocessing
import time
from spearmint.schema import Experiment as Exp
import subprocess
# from spearmint.main import *
import signal
from path_config import *
from sqlobject import *
import requests
from cloudbench.env.clouds.config import Config



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
##############################################################################################################

def get_controllerip():
    return Config.controllerip

def get_project_id():
    return Config.project_id

def get_user_id():
    return Config.user_id

def get_keystone_authtoken():
    controllerip = get_controllerip()
    payload = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "id": get_user_id(),
                        "password": "admin"
                    }
                }
            },
            "scope": {
                "project": {
                    "id": get_project_id()
                }
            }
        }
    }
    response = requests.post("http://" + controllerip + ":5000/v3/auth/tokens", json=payload)
    return response.headers["X-Subject-Token"]

def get_cluster_name():
    clusters_name_list = []
    token = get_keystone_authtoken()
    header = {
        "X-Auth-Token": token
    }
    response = requests.get("http://" + Config.controllerip +
                            ":8386/v1.1/" + get_project_id() + "/clusters", headers=header)
    clusters = response.json()["clusters"]

    for i in range(len(clusters)):
        clusters_name_list.append(clusters[i]["name"])
    return clusters_name_list

def get_search_name():
    return Config.search_name

def get_master_ip(count):
    token = get_keystone_authtoken()
    header = {
        "X-Auth-Token": token
    }
    response = requests.get("http://" + Config.controllerip +
                            ":8386/v1.1/" + get_project_id()+ "/clusters", headers=header)
    clusters = response.json()["clusters"]
    node_groups = clusters[count]["node_groups"]
    instances = node_groups[0]["instances"]
    master_ip = instances[0]["management_ip"]
    print master_ip
    return master_ip


def cluster_exist(str):
    cluster_name_list = get_cluster_name()
    count = 0
    for i in range(len(cluster_name_list)):
        if str == cluster_name_list[i]:
            break
        else:
            count = count + 1
    if count == len(cluster_name_list):
        return False
    else:
        get_master_ip(count)

def check_or_create_cluster(vm, cluster_size):
    # TODO: check if the cluster exists

    command = EXE_PATH + "/setup.sh 0 terasort " + vm + " " + str(cluster_size)
    print os.system(command)


###############################################################################################################
# Phase 3:
###############################################################################################################


def find_and_update_run(vm, cluster_size, exp_name, time):
    exp = Exp.find(exp_name)
    runs = exp.find_runs(vm, int(cluster_size))
    if time != -1:
        runs[0].time = runs[0].time * GAMMA + (1 - GAMMA) * time
        runs[0].num = 1
    print vm
    print runs
    return runs[0]

# find_and_update_run("c3.xlarge", 2, "terasort", 50)


if __name__ == '__main__':
    exp_name, vm, cluster_size = select_configuration("user1", "job", "2", True)
    # find_and_update_run("c3.xlarge", 2, "terasort", 50)
    print exp_name, vm, cluster_size
    # check_or_create_cluster(vm, cluster_size)
    # print "cluster"
