import subprocess
import base64

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

class OpenstackCloud(Cloud):

    controllerip = Config.controllerip

    def __init__(self, *args, **kwargs):
        super(OpenstackCloud, self).__init__(*args, **kwargs)
        constants.DEFAULT_VM_USERNAME = 'ubuntu'
        constants.DEFAULT_VM_PRIVATE_KEY= '/home/cherry.pem'

    def execute(self, command, obj={}):
        ret = super(OpenstackCloud, self).execute(command, obj)
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
        return vm.name

    def hashify_22(self, name):
        import hashlib
        return str(hashlib.md5(name).hexdigest())[0:22]

    def create_location(self, group):
        return True

    def create_security_group(self, ep):
        return True

    def create_virtual_machine(self, vm):
        self.create_server(vm.name, vm._config['image'], vm._config['type'])
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

    # def get_projectid(self):
    #     token = self.getKeystoneAuthToken()
    #     header = {
    #         "X-Auth-Token": token
    #     }
    #     response = requests.get("http://" + self.controllerip + ":5000/v3/projects", headers=header)
    #     project_id = None
    #     projects = response.json()['projects']
    #     for project in projects:
    #         if (project['name'] == 'admin'):
    #             project_id = project['id']
    #         return project_id

    def get_image_id(self, image_name):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":9292/v2/images", headers=header)
        print(response.text)
        images = response.json()['images']
        for image in images:
            if image['name'] == image_name:
                id = image['id']
                return id

    def get_network_id(self, net_name):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":9696/v2.0/networks", headers=header)
        networks = response.json()['networks']
        for network in networks:
            if( network['name'] == net_name and network['tenant_id'] == self.get_projectid() ):
                return network['id']

    def get_flavor_id(self, flavor_name):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":8774/v2/flavors/detail", headers=header)
        flavors = response.json()['flavors']
        # print "ID" + "|" + "name" + "|" + "ram" + "|" + "disk" + "|" + "vcpus" + "|" + "rxtx" + "|" + "ispublic"
        for flavor in flavors:
            if flavor['name'] == flavor_name:
                return flavor['id']

    def get_secgroup_list(self):
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        response = requests.get("http://" + self.controllerip + ":9696/v2.0/security-groups", headers=header)
        secgroups = response.json()['security_groups']
        for secgroup in secgroups:
            id = secgroup['id']
            name = secgroup['name']
            description = secgroup['description']
            return id

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
                private_addresses = addresses['private']
                for private_address in private_addresses:
                    if (private_address['OS-EXT-IPS:type'] == 'floating'):
                        return private_address['addr']
        return None

    def create_server(self, vm_name, image_name, flavor_name):
        # flavor_name = "m1.tiny"
        net_name = "public"
        # image_name = "cirros-0.3.4-x86_64-uec-ramdisk"
        token = self.get_keystone_authtoken()
        header = {
            "X-Auth-Token": token
        }
        payload = {
            "server": {
                "name": vm_name,
                "imageRef": self.get_image_id(image_name),
                "flavorRef": self.get_flavor_id(flavor_name),
                "availability_zone": self.get_availability_zone(),
                "OS-DCF:diskConfig": self.get_diskConfig(),
                "key_name": self.get_key_name(),
                "security_groups": [
                    {
                        "name": self.get_security_groups()
                    }
                ],
                "networks": [
                    {
                        "uuid": self.get_network_id(self.get_network_name())
                        # "uuid": 'e19a18c8-61be-4859-b31e-c66a698fa71e'
                    }
                ]
            }
        }
        response = requests.post("http://" + self.controllerip + ":8774/v2.1/" +
                                 self.get_projectid() + "/servers", json=payload, headers=header)
        server = response.json()
        print(response.text)
        server_id = server['server']['id']
        self.associate_floating_ip(server_id)
        time.sleep(10)
        flag = self.get_url_of_instance(vm_name)
        while( flag == None ):
            print(vm_name)
            time.sleep(2)
            self.associate_floating_ip(server_id)
            flag = self.get_url_of_instance(vm_name)

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


