import shutil
import re
import math
import multiprocessing

from env_config import *
from spearmint.schema import JobInfo

from spearmint import main as bo
import openstack_api
from experiment import VirtualMachine, Experiment


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


def replace_exp(old_path, new_path, file_name, experiment):
    read_file = open(os.path.join(old_path, file_name), "r")
    write_file = open(os.path.join(new_path, file_name), "w")

    if file_name == "config.pb":
        for line in read_file.readlines():
            new_line = re.sub("template", experiment.name, line)
            write_file.write(new_line)

    elif file_name == "experiment_config.py":
        for line in read_file.readlines():
            new_line = re.sub("template", experiment.job_id, line)
            new_line = re.sub("user_id", experiment.user_id, new_line)
            new_line = re.sub("data_size", str(experiment.data_group), new_line)
            write_file.write(new_line)

    read_file.close()
    write_file.close()


def rename_exp(path, exp_name):
    template_name = os.path.join(path, "template.py")
    dst_name = os.path.join(path, exp_name + ".py")
    os.rename(template_name, dst_name)


def check_or_create_experiment(experiment):

    exp_path = os.path.join(EXP_PATH, experiment.name)
    print exp_path
    if not os.path.exists(exp_path):
        copy_tree(TEMPLATE_PATH, exp_path)

        rename_exp(exp_path, experiment.name)
        replace_exp(TEMPLATE_PATH, exp_path, "config.pb", experiment)
        replace_exp(TEMPLATE_PATH, exp_path, "experiment_config.py", experiment)

        # write the new experiment into DB
        try:
            print experiment.job_id, experiment.user_id, experiment.cpu_percentage, experiment.io_percentage
            new_experiment = JobInfo(name=experiment.job_id,
                                     user_id=experiment.user_id,
                                     cpu_percentage=experiment.cpu_percentage,
                                     io_percentage=experiment.io_percentage)
            print new_experiment
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
        print "Starting BO..."
        p.start()


def get_vm_name(io_weight, cpu_weight, vcpus, ram, disk):
    flavors = openstack_api.get_flavor_details()
    print flavors
    min_distance = -1
    vm_name = ''
    for flavor in flavors:
        if flavor['name'] not in VirtualMachine.flavor_space:
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


def get_best_config(experiment, is_to_optimize=True):
    if is_to_optimize:
        file_name = "experiment.txt"
    else:
        file_name = "best_job_and_result.txt"

    file_path = os.path.join(EXP_PATH, experiment.name, file_name)

    while not os.path.exists(file_path):
        continue

    file_object = open(file_path, 'r')
    data = file_object.read()

    if is_to_optimize:
        vm_name, vcpus, ram, disk, cluster_size, exp = data.split(' ')
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
        vm_name = get_vm_name(experiment.io_percentage, experiment.cpu_percentage, int(vcpus), int(ram), int(disk))

    experiment.set_best_configuration(int(cluster_size), vm_name, int(vcpus), int(ram), int(disk))
    return experiment


def select_configuration(experiment, is_to_optimize=True):

    check_or_create_experiment(experiment)
    start_bo(experiment.name)
    get_best_config(experiment, is_to_optimize)

    return experiment.best_configuration


# job_id = "terasort"
# data_size = 0
# user_id = "class_test1"
#
# print user_id, job_id
# experiment = Experiment(job_id, user_id, data_size)
# print experiment.job_id, experiment.user_id
# experiment.set_io_cpu_percentage()
#
# check_or_create_experiment(experiment)