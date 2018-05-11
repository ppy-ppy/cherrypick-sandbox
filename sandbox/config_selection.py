import os
import shutil
import re
import math
import multiprocessing

from env_config import *
from spearmint.schema import Experiment as Exp

from spearmint import main as bo
import openstack_api


def clean_path(path):
    path = path.strip()
    path = path.rstrip("\\")

    return path


def copy_tree(old_path, new_path):
    old_path = clean_path(old_path)
    new_path = clean_path(new_path)

    if not os.path.exists(old_path):
        print old_path + ' does not exist!'
        return False

    if os.path.exists(new_path):
        print new_path + ' already exists!'
        return False

    shutil.copytree(old_path, new_path)
    return True


def replace_exp(old_path, new_path, file_name, exp_name, job_id):
    read_file = open(os.path.join(old_path, file_name), "r")
    write_file = open(os.path.join(new_path, file_name), "w")

    key_name = "template"
    key_id = "job_id"
    for line in read_file.readlines():
        new_line = re.sub(key_name, exp_name, line)
        new_line = re.sub(key_id, job_id, new_line)
        write_file.write(new_line)


def rename_exp(path, exp_name):
    template_name = os.path.join(path, "template.py")
    dst_name = os.path.join(path, exp_name + ".py")
    os.rename(template_name, dst_name)


def create_experiment(job_id, exp_name, exp_path):
    copy_tree(TEMPLATE_PATH, exp_path)
    rename_exp(exp_path, exp_name)
    replace_exp(TEMPLATE_PATH, exp_path, "config.pb", exp_name, job_id)
    replace_exp(TEMPLATE_PATH, exp_path, "experiment_config.py", exp_name, job_id)

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
        p = multiprocessing.Process(name="BO_process", target=bo.main, args=(config_path,))
        # print "Starting BO..."
        p.start()
        # print p.pid
        # print p.name
        # bo.main(config_path)


def get_vm_name(io_weight, cpu_weight, vcpus, ram, disk):
    flavors = openstack_api.get_flavor_details()
    print flavors
    min_distance = -1
    vm_name = ''
    for flavor in flavors:
        if flavor['name'] not in flavor_space:
            continue
        if flavor['vcpus'] < vcpus or flavor['ram'] / 1024 < ram or flavor['disk'] < disk:
            continue
        else:
            distance = math.sqrt(((1 + cpu_weight) * (flavor['vcpus'] - vcpus))**2 +
                                 ((1 + io_weight) * (flavor['ram'] / 1024 - ram))**2 +
                                 (flavor['disk'] - disk)**2)
            if min_distance == -1 or distance < min_distance:
                min_distance = distance
                vm_name = flavor['name']
    if vm_name == '':
        raise Exception("No valid flavor!")

    return vm_name


def get_best_config(exp_name, io_weight, cpu_weight, is_to_optimize=True):
    if is_to_optimize:
        file_name = "experiment.txt"
    else:
        file_name = "best_job_and_result.txt"

    file_path = os.path.join(EXP_PATH, exp_name, file_name)

    while not os.path.exists(file_path):
        continue

    file_object = open(file_path, 'r')
    data = file_object.read()

    if is_to_optimize:
        vm, vcpus, ram, disk, cluster_size, exp = data.split(' ')
    else:
        data = data.split("Parameters: \n")
        print data
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
        vm = get_vm_name(io_weight, cpu_weight, int(vcpus), int(ram), int(disk))
    return vm, int(cluster_size), int(vcpus), int(ram), int(disk) * 10


def select_configuration(user_id, job_id, data_size, timestamp, io_weight, cpu_weight, is_to_optimize=True):

    data_group = "0"
    for split in data_split:
        if float(data_size) - split < 0:
            break
        data_group = str(split)

    exp_name = user_id + "-" + job_id + "-" + data_group + "-" + timestamp
    exp_path = os.path.join(EXP_PATH, exp_name)
    if not os.path.exists(exp_path):
        create_experiment(job_id, exp_name, exp_path)
    start_bo(exp_name)
    vm, cluster_size, vcpus, ram, disk = get_best_config(exp_name, io_weight, cpu_weight, is_to_optimize)

    return exp_name, vm, cluster_size, vcpus, ram, disk
