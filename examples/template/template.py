from spearmint.schema import *
from experiment_config import *
import math
import time
import requests
# from spearmint.env_config import *


# def get_vm_name(vm_type, vm_size):
#     vm_type = vm_type[0]
#     vm_size = vm_size[0]
#
#     prefix = vm_type
#     suffix = vm_size
#
#     vm_name = ".".join([prefix, suffix])
#
#     if vm_name not in flavor_space:
#         raise Exception("Invalid Machine Type!")
#
#     return vm_name
#
#
# def is_valid_cluster_size(cluster_size):
#     if cluster_size in machine_space:
#         return True
#     return False


def get_keystone_authtoken():
    payload = {
        "auth": {
            "identity": {
                "methods": [
                    "password"
                ],
                "password": {
                    "user": {
                        "id": user_id,
                        "password": "admin"
                    }
                }
            },
            "scope": {
                "project": {
                    "id": project_id
                }
            }
        }
    }
    response = requests.post("http://" + controller_ip + ":5000/v3/auth/tokens", json=payload)
    return response.headers["X-Subject-Token"]


def get_flavor_details():
    token = get_keystone_authtoken()
    header = {
        "X-Auth-Token": token
    }
    response = requests.get("http://" + controller_ip + ":8774/v2/flavors/detail", headers=header)
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


def get_cost(spec):
    vcpus = spec['vcpus']
    ram = spec['ram']
    disk = spec['disk']
    cluster_size = spec['machine_count']
    total_cost = 0.0
    print vcpus, ram, disk, cluster_size
    # if not is_valid_cluster_size(int(cluster_size)):
    #     raise Exception("Invalid Machine Count!")

    vm = get_vm_name(vcpus, ram, disk)

    vm_0 = VirtualMachineType.selectBy(name=vm).getOne()

    try:
        config = Configuration.selectBy(vm=vm_0, count=int(cluster_size)).getOne()
    except:
        Configuration(vm=vm_0, count=int(cluster_size))
        config = Configuration.selectBy(vm=vm_0, count=int(cluster_size)).getOne()

    # benchmark meta jobs
    # for i in range(5):
    #     if WEIGHT[i] == 0:
    #         continue
    #
    #     exp = Experiment.find(EXPERIMENT[i])
    #     print EXPERIMENT[i]
    #
    #     data = vm + " " + str(cluster_size[0]) + " " + EXPERIMENT[i]
    #     file_path = os.path.join(EXP_PATH, EXP_TYPE, "experiment.txt")
    #     print file_path
    #     file_object = open(file_path, 'w')
    #     file_object.write(data)
    #     file_object.close()
    #
    #     print "experiment: ", exp
    #     runs = exp.find_runs(vm, int(cluster_size))
    #     print "runs: ", runs
    #
    #     if not runs:
    #         num = 0
    #         run_time = 0
    #         Run(exp=exp, config=config, time=run_time, num=num)
    #         runs = exp.find_runs(vm, int(cluster_size))
    #
    #     for j in range(WEIGHT[i]):
    #         while runs[0].num != 1:
    #             time.sleep(5)
    #             runs = exp.find_runs(vm, int(cluster_size))
    #             print runs[0]
    #
    #         runs[0].num = 0
    #
    #         if TIME_LIMIT != -1 and runs[0].time > TIME_LIMIT:
    #             raise Exception("Run Time Exceeds!")
    #         total_cost += math.log(runs[0].cost) * runs[0].time

    # single experiment as a whole
    exp = Experiment.find(EXP_TYPE)

    data = vm + " " + \
           str(vcpus[0]) + " " + str(ram[0]) + " " + str(disk[0]) + " " + str(cluster_size[0]) + " " +\
           EXP_TYPE
    file_path = os.path.join(EXP_PATH, EXP_TYPE, "experiment.txt")
    print file_path
    file_object = open(file_path, 'w')
    file_object.write(data)
    file_object.close()

    print "experiment: ", exp
    runs = exp.find_runs(vm, int(cluster_size))
    print "runs: ", runs

    if not runs:
        num = 0
        run_time = 0
        Run(exp=exp, config=config, time=run_time, num=num)
        runs = exp.find_runs(vm, int(cluster_size))

    while runs[0].num != 1:
        time.sleep(5)
        runs = exp.find_runs(vm, int(cluster_size))
        print runs[0]

    runs[0].num = 0

    if TIME_LIMIT != -1 and runs[0].time > TIME_LIMIT:
        raise Exception("Run Time Exceeds!")
    total_cost += math.log(runs[0].cost) * runs[0].time

    print "total cost: ", total_cost
    exp_type = Experiment.find(EXP_TYPE)
    if exp_type.count > 0:
        exp_type.count -= 1
    return total_cost


def main(job_id, params):
    return COST_FUNC(get_cost(params))

#
# if __name__ == '__main__':
#     vm_name = get_vm_name(15, 15, 20)
#     print vm_name
