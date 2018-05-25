import os
from model_built import read_training_data, vm_name_list, write_file

FILE_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(FILE_PATH, "data_grouping_test.csv")

# machine_choices = [4, 8, 16]


def get_machine_choices(input_data):
    machine_choices = []
    for row in input_data:
        machines = row[0]
        if machines not in machine_choices:
            machine_choices.append(int(machines))

    return machine_choices


def generate_testing_data(training_data_path, lowest, highest):
    training_data = read_training_data(training_data_path)
    flavor_list = vm_name_list(training_data)
    machine_choices = get_machine_choices(training_data)

    if os.path.exists(TEST_PATH):
        os.remove(TEST_PATH)

    test_data = []
    for flavor in flavor_list:
        for data_size in range(lowest, highest, 1):
            for machine in machine_choices:
                data = [machine, data_size, flavor]
                write_file(TEST_PATH, data)
                test_data.append(data)

    return test_data

