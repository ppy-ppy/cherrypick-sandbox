import csv
import os
import math
from sqlobject import *
import pickle
import shutil

import sys
FILE_PATH = os.path.abspath(os.path.dirname(__file__))
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(FILE_PATH)))
sys.path.append(ROOT_PATH)

from spearmint.schema import VirtualMachineType as VM
from ernest.nnls_predictor import NnlsPredictor
from sandbox.openstack_api import *


SPLIT_PATH = os.path.join(FILE_PATH, "split_data")
TEST_PATH = os.path.join(FILE_PATH, "test.csv")
MODEL_PATH = os.path.join(FILE_PATH, "model")
CANDIDATE_PATH = os.path.join(FILE_PATH, "predicted_candidates.csv")
MAX_VALUE = 1000000000000
machine_choices = [2, 4, 8, 16]


def write_file(file_path, data):
    with open(file_path, 'a+') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)


def read_file(file_path):
    data = []
    with open(file_path, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)

    return data


def read_training_data(data_file):
    training_data = []
    with open(data_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        for row in reader:
            if row[0][0] != '#':
                parts = row[0].split(',')
                vm_type = str(parts[3])
                mc = int(parts[0])
                scale = float(parts[1])
                time = float(parts[2])
                training_data.append([mc, scale, time, vm_type])

    return training_data


# def vm_name_list(data):
#     flavor = get_flavor_details()
#     u_name = []
#     for i in range(len(flavor)):
#         u_name.append(flavor[i][u'name'])  # get the type of the mcs
#
#     data_list = []
#     for row in data:
#         data_list.append(row)  # get the csv file
#     u_list = []
#     for m in range(len(u_name)):
#         for row in data_list:
#             if row[3] == u_name[m]:
#                 u_list.append(u_name[m])
#                 break
#             else:
#                 continue
#
#     return u_list


def get_available_flavors(data):
    candidate_flavors = VM.select()
    valid_flavor_names = []
    for vm in list(candidate_flavors):
        valid_flavor_names.append(vm.name)

    available_flavors = []
    for row in data:
        flavor_name = row[3]
        if flavor_name in valid_flavor_names and flavor_name not in available_flavors:
            available_flavors.append(flavor_name)

    return available_flavors


def train_data(training_data):
    flavor_list = get_available_flavors(training_data)

    model_set = []
    if os.path.exists(SPLIT_PATH):
        shutil.rmtree(SPLIT_PATH)
    os.mkdir(SPLIT_PATH)
    split_data(training_data, flavor_list)

    for flavor in flavor_list:
        data_file = flavor + ".csv"
        file_path = os.path.join(SPLIT_PATH, data_file)
        pred = NnlsPredictor(flavor, data_file=file_path)
        sub_training_data = read_training_data(file_path)
        pred.fit(sub_training_data)
        model_set.append(pred)

    with open(MODEL_PATH, 'w') as f:
        pickle.dump(model_set, f)
    return model_set


def generate_testing_data(training_data_path, data_size,
                          machine_lowest, machine_highest, machine_interval):
    training_data = read_training_data(training_data_path)
    flavor_list = get_available_flavors(training_data)

    if os.path.exists(TEST_PATH):
        os.remove(TEST_PATH)

    test_data = []
    for i in range(len(flavor_list)):
        for machine_count in range(machine_lowest, machine_highest, machine_interval):
            if machine_count in machine_choices:
                data = [machine_count, data_size, flavor_list[i]]
                write_file(TEST_PATH, data)
                test_data.append([machine_count, data_size, flavor_list[i]])

    return test_data


def get_model(model_name):
    with open(MODEL_PATH, 'r') as f:
        model_set = pickle.load(f)

    for model in model_set:
        if model.name == model_name:
            return model


def check_valid_scale(scale, flavor_name):
    disk = VM.selectBy(name=flavor_name).getOne().root_disk
    max_valid_scale = int(disk) / 6
    if scale > max_valid_scale:
        return False

    return True


def test_data(testing_data):

    if os.path.exists(CANDIDATE_PATH):
        os.remove(CANDIDATE_PATH)

    for row in testing_data:
        machine_count = int(row[0])
        data_size = float(row[1])
        flavor_name = str(row[2])
        pred_model = get_model(flavor_name)
        predicted_time = pred_model.predict(machine_count, data_size)
        # if check_valid_scale(data_size, flavor_name):
        #     predicted_time = pred_model.predict(machine_count, data_size)
        # else:
        #     predicted_time = -2

        content = machine_count, data_size, predicted_time, flavor_name
        write_file(CANDIDATE_PATH, content)


def split_data(data, flavor_list):
    for i in range(len(flavor_list)):
        for row in data:
            flavor_name = row[3]
            data_file = flavor_name + ".csv"
            file_path = os.path.join(SPLIT_PATH, data_file)
            content = [int(row[0]), float(row[1]), float(row[2]), str(row[3])]
            write_file(file_path, content)


def ddl_in_time_predicted(candidate_data, deadline):
    in_time_data = []

    for row in candidate_data:
        run_time = row[2]
        if run_time <= deadline:
            in_time_data.append(row)

    return in_time_data


def ddl_get_lowest_cost(deadline):
    candidate_data = read_training_data(CANDIDATE_PATH)
    in_time_data = ddl_in_time_predicted(candidate_data, deadline)
    min_cost = MAX_VALUE
    lowest = ""

    for row in in_time_data:
        machine_count = row[0]
        predicted_time = row[2]
        flavor_name = row[3]
        price = VM.selectBy(name=flavor_name).getOne().cost
        if predicted_time == -2:
            continue
        cost = math.log(price * machine_count) * predicted_time
        if cost < min_cost:
            min_cost = cost
            lowest = row

    return lowest, math.log(min_cost)




