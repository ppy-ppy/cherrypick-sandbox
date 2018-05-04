import os

import openstack_api
from env_config import *


def cluster_exist(cluster_name):
    cluster_name_list = openstack_api.get_cluster_name()
    count = 0
    for i in range(len(cluster_name_list)):
        if cluster_name == cluster_name_list[i]:
            break
        else:
            count = count + 1
    if count == len(cluster_name_list):
        return False
    else:
        return openstack_api.get_master_ip(count)


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
