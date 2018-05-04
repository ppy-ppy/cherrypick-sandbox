import multiprocessing
import sys

import requests

from cloudbench.env.clouds.config import Config
from env_config import *
from ernest.output_data import *
from spearmint.schema import Experiment as Exp
from runtest import *
from spearmint import main as bo
from classifier import main as job_classifier

print sys.path

###############################################################################################################
# Phase 1: Create the experiment (if new), start BO, and return the next sample/current best configuration.
###############################################################################################################


def softmax_application_classifier(input_data):
    (io_weight, cpu_weight), job_class = job_classifier.softmax_classifier(input_data)
    return (io_weight, cpu_weight), job_class


###############################################################################################################
# Phase 2: Create the experiment (if new), start BO, and return the next sample/current best configuration.
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
        # p = multiprocessing.Process(name="BO_process", target=os.system, args=(command_,))
        # print "Starting BO..."
        # p.start()
        # print p.pid
        # print p.name
        bo.main(config_path)


def get_flavor_details():
    token = get_keystone_authtoken()
    header = {
        "X-Auth-Token": token
    }
    response = requests.get("http://" + Config.controllerip + ":8774/v2/flavors/detail", headers=header)
    flavors = response.json()['flavors']
    return flavors


def get_vm_name(vcpus, ram, disk):
    flavors = get_flavor_details()
    print flavors
    min_distance = -1
    vm_name = ''
    for flavor in flavors:
        if flavor['vcpus'] < vcpus or flavor['ram'] / 1024 < ram or flavor['disk'] < disk:
            continue
        else:
            distance = math.sqrt((flavor['vcpus'] - vcpus)**2 +
                                 (flavor['ram'] / 1024 - ram)**2 +
                                 (flavor['disk'] - disk)**2)
            if min_distance == -1 or distance < min_distance:
                min_distance = distance
                vm_name = flavor['name']
    if vm_name == '':
        raise Exception("No valid flavor!")

    return vm_name


def get_best_config(exp_name, is_to_optimize=True):
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
        vm, vcpus, ram, disk, cluster_size, exp = data.split(' ')
    else:
        data = data.split("Parameters: \n")
        lines = data[1].split("\n")
        data = ""
        for line in lines:
            line = line.replace("name: ", '')
            line = line.replace("int_val: ", '')
            line = line.replace('"', '')
            line = line.replace("\n", "")
            line = line.replace("vcpus", "")
            line = line.replace("ram", ", ")
            line = line.replace("disk", ", ")
            line = line.replace("machine_count", ", ")
            data += line

        vcpus, ram, disk, cluster_size = data.split(", ")
        vm = get_vm_name(int(vcpus), int(ram), int(disk))
    return vm, int(vcpus), int(ram), int(disk), int(cluster_size)


def select_configuration(user_id, job_id, data_size, timestamp, is_to_optimize=True):

    data_group = "0"
    for split in data_split:
        if float(data_size) - split < 0:
            break
        data_group = str(split)

    exp_name = user_id + "-" + job_id + "-" + data_group + "-" + timestamp
    exp_path = os.path.join(EXP_PATH, exp_name)
    if not os.path.exists(exp_path):
        create_experiment(exp_name, exp_path)
    start_bo(exp_name)
    vm, vcpus, ram, disk, cluster_size = get_best_config(exp_name, is_to_optimize)

    return exp_name, vm, vcpus, ram, disk, cluster_size


###############################################################################################################
# Phase 3: Check if the cluster under selected configuration exists. If not, create it.
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


def get_master_ip(count):
    token = get_keystone_authtoken()
    header = {
        "X-Auth-Token": token
    }
    response = requests.get("http://" + Config.controllerip +
                            ":8386/v1.1/" + get_project_id() + "/clusters", headers=header)
    clusters = response.json()["clusters"]
    node_groups = clusters[count]["node_groups"]
    instances = node_groups[0]["instances"]
    master_ip = instances[0]["management_ip"]
    print master_ip
    return master_ip


def cluster_exist(cluster_name):
    cluster_name_list = get_cluster_name()
    count = 0
    for i in range(len(cluster_name_list)):
        if cluster_name == cluster_name_list[i]:
            break
        else:
            count = count + 1
    if count == len(cluster_name_list):
        return False
    else:
        return get_master_ip(count)


def check_or_create_cluster(vm, cluster_size):
    prefix, suffix = vm.split('.')
    cluster_name = prefix + "-" + suffix + "-" + cluster_size
    print cluster_name
    ip_address = cluster_exist(cluster_name)
    if not ip_address:
        command = EXE_PATH + "/setup.sh 0 terasort " + vm + " " + str(cluster_size)
        print os.system(command)
        return False
    else:
        return ip_address


###############################################################################################################
###############################################################################################################


def find_and_update_run(vm, cluster_size, exp_name, time):
def find_and_update_run(vm, cluster_size, exp_name, time, scale):
    exp = Exp.find(exp_name)
    runs = exp.find_runs(vm, int(cluster_size))
    if float(time) != -1:
        runs[0].time = runs[0].time * GAMMA + (1 - GAMMA) * float(time)
        runs[0].num = 1
        # print vm
    # print runs
    output_test_time_ernest(vm, int(cluster_size), exp_name, float(time))
    output_test_time_ernest(vm, int(cluster_size), exp_name, float(time), str(scale))
    return runs[0]


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
