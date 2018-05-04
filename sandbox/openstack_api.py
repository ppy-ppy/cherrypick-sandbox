import requests
from cloudbench.env.clouds.config import Config


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


def get_flavor_details():
    token = get_keystone_authtoken()
    header = {
        "X-Auth-Token": token
    }
    response = requests.get("http://" + Config.controllerip + ":8774/v2/flavors/detail", headers=header)
    flavors = response.json()['flavors']
    return flavors