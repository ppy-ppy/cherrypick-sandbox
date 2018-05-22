import csv
import os
import math
from sqlobject import *
from spearmint.schema import VirtualMachineType as VM
from nnls_predictor import Nnls_Predictor
from sandbox.openstack_api import *
import pickle
import shutil


FILE_PATH = os.path.abspath(os.path.dirname(__file__))
# ERNEST_PATH = os.path.abspath(os.path.dirname(FILE_PATH))
# ERNEST_PATH = os.path.join(ROOT_PATH, "ernest")

SPLIT_PATH = os.path.join(FILE_PATH, "split_data")
TEST_PATH = os.path.join(FILE_PATH, "test.csv")
INPUT_PATH = os.path.join(FILE_PATH, "experiment_data.csv")
MODEL_PATH = os.path.join(FILE_PATH, "model")
COMPARE_PATH = os.path.join(FILE_PATH, "compare.csv")
MAX_VALUE = 1000000000000
deadline = 60


def generate_testing_data(lowest, highest, interval, machine_lowest, machine_highest, machine_interval):
    training_data = read_training_data(INPUT_PATH)
    flavor_list = vm_name_list(training_data)

    if os.path.exists(TEST_PATH):
        os.remove(TEST_PATH)

    test_data = []
    for i in range(len(flavor_list)):
        for machine_count in range(machine_lowest, machine_highest, machine_interval):
            for data_size in range(lowest, highest, interval):
                if (machine_count == 4) or (machine_count == 8) or (machine_count == 16) or (machine_count == 2):
                    data = [machine_count, data_size, flavor_list[i]]
                    write_file(TEST_PATH, data)
                    test_data.append([machine_count, data_size, flavor_list[i]])

    # print test_data
    # write_file(TEST_PATH, test_data)
    return test_data


def get_model(model_name):
    with open(MODEL_PATH, 'r') as f:
        model_set = pickle.load(f)

    for model in model_set:
        if model.name == model_name:
            return model


def test_data(testing_data):
    # testing_data = read_file(TEST_PATH)

    if os.path.exists(COMPARE_PATH):
        os.remove(COMPARE_PATH)

    # print test_data
    for row in testing_data:
        # data = row.split(',')
        # print data
        machine_count = int(row[0])
        data_size = float(row[1])
        flavor_name = str(row[2])
        pred_model = get_model(flavor_name)

        predicted_time = pred_model.predict(machine_count, data_size)

        content = machine_count, data_size, predicted_time, flavor_name
        write_file(COMPARE_PATH, content)

    # print test_data
    # print '\n'
    # print predicted_times
    #
    # for j in range(len(test_data)):
    #     compare_data.append([test_data[j][0], test_data[j][1], predicted_times[j], vm_name_list_all[i]])
    #     print compare_data[j]
    #     print '\n'


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


def split_data(data, flavor_list):
    for i in range(len(flavor_list)):
        for row in data:
            flavor_name = row[3]
            data_file = flavor_name + ".csv"
            file_path = os.path.join(SPLIT_PATH, data_file)
            content = [int(row[0]), float(row[1]), float(row[2]), str(row[3])]
            write_file(file_path, content)


def ddl_in_time_predicted(compare_data):
    in_time_data = []

    for row in compare_data:
        # print row
        # data = row.split(',')
        # print data
        run_time = row[2]
        if run_time <= deadline:
            in_time_data.append(row)
    #
    # for i in range(len(compare_data)):
    #     if compare_data[i][2] <= deadline:
    #         in_time_data.append(compare_data[i])
    #         # del predictor_data[i]
    #     else:
    #         continue
    return in_time_data


def ddl_get_lowest_cost():
    compare_data = read_training_data(COMPARE_PATH)
    in_time_data = ddl_in_time_predicted(compare_data)
    min_cost = MAX_VALUE
    lowest = ""
    # lowest_cost_configuration = []

    for row in in_time_data:
        machine_count = row[0]
        predicted_time = row[2]
        flavor_name = row[3]
        price = VM.selectBy(name=flavor_name).getOne().cost
        cost = math.log(price) * machine_count * predicted_time
        if cost < min_cost:
            min_cost = cost
            lowest = row


    # for i in range(len(in_time_data)):
    #     price = VM.selectBy(name = in_time_data[i][3]).getOne().cost
    #     cost.append(math.log(price)*in_time_data[i][0]*in_time_data[i][2])
    #     # cost.append(in_time_data[i][0]*in_time_data[i][1]*price)

    # lowest_cost = min(cost)
    # a = cost.index(lowest_cost)
    # lowest_cost_configuration.append(in_time_data[a][0])
    # lowest_cost_configuration.append(in_time_data[a][1])
    # lowest_cost_configuration.append(lowest_cost)
    # lowest_cost_configuration.append(in_time_data[a][3])
    return lowest, min_cost


def vm_name_list(data):
    flavor = get_flavor_details()
    u_name = []
    for i in range(len(flavor)):
        u_name.append(flavor[i][u'name'])  # get the type of the mcs
    print u_name

    data_list = []
    for row in data:
        data_list.append(row)  # get the csv file
    u_list = []
    for m in range(len(u_name)):
        for row in data_list:
            if row[3] == u_name[m]:
                u_list.append(u_name[m])
                break
            else:
                continue
    print '\n'

    print u_list

    return u_list


def train_data(training_data):
    training_data = read_training_data(INPUT_PATH)
    flavor_list = vm_name_list(training_data)

    model_set = []
    # TODO: delete all sub-files (*.csv)
    # split_path = os.path.join(ERNEST_PATH, "job_id", "split_data")
    if os.path.exists(SPLIT_PATH):
        shutil.rmtree(SPLIT_PATH)
    os.mkdir(SPLIT_PATH)
    split_data(training_data, flavor_list)

    for flavor in flavor_list:
        data_file = flavor + ".csv"
        file_path = os.path.join(SPLIT_PATH, data_file)
        pred = Nnls_Predictor(flavor, data_file=file_path)
        sub_training_data = read_training_data(file_path)
        model = pred.fit(sub_training_data)
        model_set.append(pred)

    with open(MODEL_PATH, 'w') as f:
        pickle.dump(model_set, f)
    # write_file(MODEL_PATH, model_set)
    return model_set


# def model_configuration1():
#
#         if len(sys.argv) != 2:
#             print "Usage <predictor.py> <csv_file_train>"
#             sys.exit(0)
#
#         train_data_list = read_file(INPUT_PATH)  # xunlian shuju
#
#         vm_name_list_all = vm_name_list(train_data_list)  # shengcheng shuju flavor
#
#         compare_data = []
#
#         model_set = []
#
#         # print '\n'
#         # print vm_name_list_all
#
#         # for i in range(len(vm_name_list_all)):
#         #
#         #     training_point = []
#         #     # machine_type = vm_name_list_all
#         #     # with open(file_name, "w") as csvfile:
#         #     #     writer = csv.writer(csvfile)
#         #     #     writer.writerow(["mc", "scale", "time", "vm_type"])
#         #     # for j in range(len(train_data_list)):
#         #     #     if train_data_list[j][5] == vm_name_list_all[i]:
#         #     #     # writer.writerow([row[0], row[3], row[4], row[5]])
#         #     #        training_point.append([train_data_list[j][0], train_data_list[j][3], train_data_list[j][4], train_data_list[j][5]])
#         #
#         #     flavor_name = vm_name_list_all[i]
#
#         split_data(train_data_list, vm_name_list_all)
#
#         for i in range(len(vm_name_list_all)):
#             pred = Pure_Predictor(vm_name_list_all[i], data_file="xxx.csv")
#             model = pred.fit(train_data_list)
#             model_set.append(model)
#
#
#         test_data(pred, vm_name_list_all, i, compare_data)
#
#         lowest_config = ddl_get_lowest_cost(compare_data)
#
#         print "The lowest configuration is "
#
#         print lowest_config


# def get_configuration(job_id):
#     exp_dir = os.path.join(ERNEST_PATH, job_id)
#     if not os.path.exists(exp_dir):
#         os.mkdir(exp_dir)




if __name__ == '__main__':
    # model_set = train_data()
    # print model_set
    #
    # testing_data = generate_data()
    # print testing_data
    # #
    # model_set = read_file(MODEL_PATH)
    # testing_data = read_file(TEST_PATH)
    # test_data(testing_data)

    # print read_file(TEST_PATH)
    #
    compare_data = read_training_data(COMPARE_PATH)
    print ddl_get_lowest_cost(compare_data)
