import subprocess
import base64
import os

from cloudbench import constants
from cloudbench.util import Debug, parallel, rate_limit

from .base import Cloud

from threading import RLock

import time
import requests
from .config import Config
import random

def disable(func):
    def func(*args, **kwargs):
        return True

    return func

def prn_obj(obj):
    print '\n'.join(['%s:%s' % item for item in obj.__dict__.items()])

class SaharaCloud(Cloud):

    controllerip = Config.controllerip
    node_count = None

    def __init__(self, *args, **kwargs):
        super(SaharaCloud, self).__init__(*args, **kwargs)
        constants.DEFAULT_VM_USERNAME = 'ubuntu'
        dir_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        key_dir = os.path.abspath(os.path.dirname(os.path.dirname(dir_path)))
        key_path = key_dir + '/cherrypick.pem'
        constants.DEFAULT_VM_PRIVATE_KEY = key_path
        self.node_count = len(args[0]._benchmark._config._entities['virtual_machines'])

    def execute(self, command, obj={}):
        ret = super(SaharaCloud, self).execute(command, obj)
        return ret

    def start_virtual_machine(self, vm):
        """ Start a virtual machine """
        vm._started = True
        return

    def stop_virtual_machine(self, vm):
        """ Stop a virtual machine """
        vm._started = False
        return True

    def status_virtual_machine(self, vm):
        return vm._started

    def exists_virtual_machine(self, vm):
        return True

    def address_virtual_machine(self, vm):
        """ Returns the address of a vm """
        node_count = self.node_count
        def get_master_nodegroup_template_name( vm ):
            raw_str = vm._config['type'].split('.')
            print raw_str[0] + '-' + raw_str[1] + '-master'
            return raw_str[0] + '-' + raw_str[1] + '-master'
        def get_slave_nodegroup_template_name( vm ):
            raw_str = vm._config['type'].split('.')
            print raw_str[0] + '-' + raw_str[1] + '-slave'
            return raw_str[0] + '-' + raw_str[1] + '-slave'
        def get_cluster_name( vm ):
            raw_str = vm._config['type'].split('.')
            print raw_str[0] + '-' + raw_str[1] + '-' + str(node_count)
            return raw_str[0] + '-' + raw_str[1] + '-' + str(node_count)
        if( vm.name == 'master' ):
            master_node_name = get_cluster_name(vm) + '-' + get_master_nodegroup_template_name(vm) + '-0'
            return self.get_url_of_instance(master_node_name)
        else:
            slave_node_base_name = get_cluster_name(vm) + '-' + get_slave_nodegroup_template_name(vm) + '-'
            str_list = vm.name.split('-')
            server_name = slave_node_base_name + str_list[1]
            return self.get_url_of_instance( server_name )


    def hashify_22(self, name):
        import hashlib
        return str(hashlib.md5(name).hexdigest())[0:22]

    def create_location(self, group):
        return True

    def create_security_group(self, ep):
        return True

    def get_cluster_template_name(self):
        return Config.cluster_template_name

    def get_cluster_template_name(self):
        return Config.cluster_template_name

    def get_cluster_name(self):
        return Config.cluster_name

    def get_get_master_nodegroup_template_name(self):
        return Config.master_nodegroup_template_name

    def get_slave_nodegroup_template_name(self):
        return Config.slave_nodegroup_template_name

    def get_master_nodegroup_template_name(self):
        return Config.master_nodegroup_template_name

    def get_slave_nodegroup_template_name(self):
        return Config.slave_nodegroup_template_name

    def get_url_of_instance(self, instance_name):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":8774/v2.1/servers/detail", headers=header)
        servers = response.json()['servers']
        for server in servers:
            if (server['name'] == instance_name):
                addresses = server['addresses']
                private_addresses = addresses['demo-net']
                for private_address in private_addresses:
                    if (private_address['OS-EXT-IPS:type'] == 'floating'):
                        return private_address['addr']
        return None

    def create_virtual_machine(self, vm):
        node_count = self.node_count
        def get_master_nodegroup_template_name( vm ):
            raw_str = vm._config['type'].split('.')
            return raw_str[0] + '-' + raw_str[1] + '-master'
        def get_slave_nodegroup_template_name( vm ):
            raw_str = vm._config['type'].split('.')
            return raw_str[0] + '-' + raw_str[1] + '-slave'
        def get_cluster_name( vm ):
            raw_str = vm._config['type'].split('.')
            return raw_str[0] + '-' + raw_str[1] + '-' + str(node_count)
        def get_cluster_template_name( vm ):
            raw_str = vm._config['type'].split('.')
            print raw_str
            return raw_str[0] + '-' + raw_str[1] + '-' + str(node_count)
        if( vm.name=="master" ):
            # Get all configs from Config
            cluster_template_name = get_cluster_template_name(vm)
            cluster_name = get_cluster_name(vm)
            image_id = self.get_image_id(vm._config['image'])
            flavor_id = self.get_flavor_id(vm._config['type'])
            master_node_count = 1
            slave_node_count = self.node_count - 1
            master_nodegroup_template_name = get_master_nodegroup_template_name(vm)
            slave_nodegroup_template_name = get_slave_nodegroup_template_name(vm)
            # Create master nodegroup template
            self.create_master_node(master_nodegroup_template_name, image_id, flavor_id)
            # Create slave nodegroup template
            self.create_slave_node(slave_nodegroup_template_name, image_id, flavor_id)
            # Create cluster template
            self.create_cluster_template(cluster_template_name, master_nodegroup_template_name,
                                         slave_nodegroup_template_name, master_node_count, slave_node_count)
            cluster_template_id = self.get_cluster_template_id(cluster_template_name)
            # Create cluster
            self.create_cluster(cluster_name, vm._config['image'], self.get_network_name(), cluster_template_id)
            time.sleep(30)
            master_node_base_name = cluster_name + '-' + master_nodegroup_template_name + '-'
            slave_node_base_name = cluster_name + '-' + slave_nodegroup_template_name + '-'
            self.associate_floating_ip(self.get_id_of_server(master_node_base_name + '0'))
            time.sleep(2)
            i=0
            while i < slave_node_count:
                self.associate_floating_ip(self.get_id_of_server(slave_node_base_name + str(i)))
                i = i+1
                time.sleep(2)
        return True

    def create_virtual_network(self, vnet):
        # prn_obj(vnet)
        return True

    def delete_security_group(self, _):
        return True

    def delete_virtual_machine(self, virtual_machine):
        return True

    def delete_virtual_network(self, vnet):
        return True

    def delete_location(self, group):
        return True

    def get_userid(self):
        return Config.user_id

    def get_projectid(self):
        return Config.project_id

    def get_user_password(self):
        return Config.password

    def get_security_groups(self):
        return Config.security_groups

    def get_diskConfig(self):
        return Config.diskConfig

    def get_availability_zone(self):
        return Config.availability_zone

    def get_network_name(self):
        return Config.network_name

    def get_key_name(self):
        return Config.key_name

    def get_plugin_name(self):
        return Config.plugin_name

    def get_hadoop_version(self):
        return Config.hadoop_version

    def get_floating_ip_pool(self):
        return Config.floating_ip_pool_id

    def get_master_node_count(self):
        return Config.master_node_count

    def get_slave_node_count(self):
        return Config.slave_node_count

    def get_keystone_authtoken(self):
        payload = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "id": self.get_userid(),
                            "password": self.get_user_password()
                        }
                    }
                },
                "scope": {
                    "project": {
                        "id": self.get_projectid()
                    }
                }
            }
        }
        response = requests.post("http://" + self.controllerip + ":5000/v3/auth/tokens", json=payload)
        return response.headers['X-Subject-Token']

    def get_flavor_id(self, flavor_name):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":8774/v2/flavors/detail", headers=header)
        flavors = response.json()['flavors']
        for flavor in flavors:
            if flavor['name'] == flavor_name:
                return flavor['id']

    def create_master_node(self, node_name, image_id, flavor_id):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        payload = {
            "plugin_name": self.get_plugin_name(),
            "hadoop_version": self.get_hadoop_version(),
            "node_processes": [
                "namenode",
                "secondarynamenode",
                "resourcemanager",
                "oozie",
                "historyserver",
                "hiveserver",
                "spark history server",
                "master"
            ],
            "name": node_name,
            "image_id": image_id,
            "flavor_id": flavor_id,
            "security_groups": [self.get_security_groups()]
        }
        response = requests.post("http://" + self.controllerip + ":8386/v1.1/" +
                                 self.get_projectid() + "/node-group-templates", json=payload, headers=header)
        if response.status_code == 200:
            return response.json()["node_group_template"]['id']

    def create_slave_node(self, node_name, image_id, flavor_id):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        payload = {
            "plugin_name": self.get_plugin_name(),
            "hadoop_version": self.get_hadoop_version(),
            "node_processes": [
                "datanode",
                "nodemanager",
                "slave"
            ],
            "name": node_name,
            "image_id": image_id,
            "flavor_id": flavor_id,
            "security_groups": [self.get_security_groups()]
        }
        response = requests.post("http://" + self.controllerip + ":8386/v1.1/" +
                                self.get_projectid() + "/node-group-templates", json=payload, headers=header)
        if response.status_code == 200:
            return response.json()["node_group_template"]['id']

    def get_nodegroup_id(self, name):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":8386/v1.1/" +
                                 self.get_projectid() + "/node-group-templates", headers=header)
        node_group_templates = response.json()['node_group_templates']
        for node_group_template in node_group_templates:
            if node_group_template['name'] == name:
                return node_group_template['id']

    def create_cluster_template(self, cluster_template_name, master_name, slave_name, master_count, slave_count):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        payload = {
            "plugin_name": self.get_plugin_name(),
            "hadoop_version": self.get_hadoop_version(),
            "node_groups": [
            {
                "name": master_name,
                "count": master_count,
                "node_group_template_id": self.get_nodegroup_id(master_name)
            },
            {
                "name": slave_name,
                "count": slave_count,
                "node_group_template_id": self.get_nodegroup_id(slave_name)
            }
            ],
            "name": cluster_template_name
}
        cluster_template_id = self.get_cluster_template_id(cluster_template_name)
        response = requests.post("http://" + self.controllerip + ":8386/v1.1/" +
                                    self.get_projectid() + "/cluster-templates", json=payload, headers=header)
        # if cluster_template_id == None:
        #     response = requests.post("http://" + self.controllerip + ":8386/v1.1/" +
        #                             self.get_projectid() + "/cluster-templates", json=payload, headers=header)
        #     print response.json()
        #     return response.json()["cluster_template"]["id"]
        # else:
        #     return cluster_template_id

    def get_cluster_template_id(self, name):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":8386/v1.1/" +
                                self.get_projectid() + "/cluster-templates", headers=header)
        cluster_templates = response.json()['cluster_templates']
        for cluster_template in cluster_templates:
            if cluster_template['name'] == name:
                return cluster_template['id']
        return None

    def get_image_id(self, image_name):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":9292/v2/images", headers=header)
        images = response.json()['images']
        for image in images:
            if image['name'] == image_name:
                id = image['id']
                return id

    def get_management_network_id(self, net_name):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":9696/v2.0/networks", headers=header)
        networks = response.json()['networks']
        for network in networks:
            if (network['name'] == net_name and network['tenant_id'] == self.get_projectid()):
                return network['id']

    def create_cluster(self, cluster_name, image_name, net_name, clu_temp_id):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        payload = {
            "plugin_name": self.get_plugin_name(),
            "hadoop_version": self.get_hadoop_version(),
            "cluster_template_id": clu_temp_id,
            "default_image_id": self.get_image_id(image_name),
            "user_keypair_id": self.get_key_name(),
            "name": cluster_name,
            "neutron_management_network": self.get_management_network_id(net_name)
        }
        response = requests.post("http://" + self.controllerip + ":8386/v1.1/" +
                                 self.get_projectid() + "/clusters", json=payload, headers=header)
        return True

    def get_id_of_server(self, name):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":8774/v2.1/servers/detail", headers=header)
        servers = response.json()['servers']
        for server in servers:
            if server['name']==name:
                return server['id']
        return None


    def associate_floating_ip(self, server_id):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        payload = {
            "addFloatingIp" :
                {
                    "address": self.get_free_floatings()
                }}
        print server_id
        response = requests.post("http://" + self.controllerip + ":8774/v2.1/servers/" +
                                 server_id + "/action", json=payload, headers=header)
        if( response.status_code == 200 ):
            return True
        else:
            return False

    def get_free_floatings(self):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":8774/v2.1/os-floating-ips", headers=header)
        floating_ips = response.json()['floating_ips']
        for floating_ip in floating_ips:
            if( floating_ip['fixed_ip'] == None ):
                return floating_ip['ip']


















