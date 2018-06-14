import itertools
import os
import shutil

from ernest.exp_grouping import Grouping

# from spearmint.schema import VirtualMachineType as VM


FILE_PATH = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.join(FILE_PATH, "data")
MODEL_PATH = os.path.join(FILE_PATH, "models")
# GROUP_PATH = os.path.join(FILE_PATH, "grouping/predicted_candidates.csv")


def create_experiment(exp_data_path, job_id, data_grouping):
    exp_dir = os.path.join(MODEL_PATH, job_id)
    if not os.path.exists(exp_dir):
        os.mkdir(exp_dir)
        init_file = os.path.join(exp_dir, '__init__.py')
        open(init_file, 'w')

        src_file = os.path.join(FILE_PATH, "model_built.py")
        dst_file = os.path.join(exp_dir, "model_built.py")
        shutil.copy(src_file, dst_file)

        src_file = os.path.join(FILE_PATH, "data_grouping.py")
        dst_file = os.path.join(exp_dir, "data_grouping.py")
        shutil.copy(src_file, dst_file)

    if data_grouping:
        file_name = job_id + "_data_grouping.csv"
    else:
        file_name = job_id + ".csv"

    src_file = os.path.join(exp_data_path)
    dst_file = os.path.join(exp_dir, file_name)
    shutil.copy(src_file, dst_file)


def train_model(job_id, data_path):
    mod = __import__("models." + job_id,
                     fromlist=['model_built', ])
    model_built = mod.model_built
    training_data = model_built.read_training_data(data_path)
    model_built.train_data(training_data)


def generate_size_restricted_data(job_id, training_data_path, data_size,
                                  machine_lowest, machine_highest, machine_interval):
    mod = __import__("models." + job_id,
                     fromlist=['model_built', ])
    model_built = mod.model_built
    model_built.generate_testing_data(training_data_path,
                                      data_size,
                                      machine_lowest, machine_highest, machine_interval)

    test_path = model_built.TEST_PATH
    testing_data = model_built.read_file(test_path)
    return testing_data


def generate_machine_restricted_data(job_id, training_data_path, lowest, highest):
    mod = __import__("models." + job_id,
                     fromlist=['data_grouping', 'model_built', ])
    data_grouping = mod.data_grouping
    model_built = mod.model_built
    data_grouping.generate_testing_data(training_data_path, lowest, highest)

    test_path = data_grouping.TEST_PATH
    testing_data = model_built.read_file(test_path)
    return testing_data


def test_model(job_id, testing_data):
    mod = __import__("models." + job_id,
                     fromlist=['model_built', ])
    model_built = mod.model_built
    model_built.test_data(testing_data)


def get_best_configuration(job_id, deadline):
    mod = __import__("models." + job_id,
                     fromlist=['model_built', ])
    model_built = mod.model_built
    lowest, min_cost = model_built.ddl_get_lowest_cost(deadline)

    return lowest, min_cost


def data_grouping(job_id, data_lowest, data_highest, test_only):
    data_grouping_file_name = job_id + "_data_grouping.csv"
    grouping_data_path = os.path.join(DATA_PATH, data_grouping_file_name)

    exp_dir = os.path.join(MODEL_PATH, job_id)
    training_data_path = os.path.join(exp_dir, data_grouping_file_name)

    if not os.path.exists(training_data_path):
        create_experiment(grouping_data_path, job_id, data_grouping=True)

    if not test_only:
        train_model(job_id, training_data_path)

    testing_data = generate_machine_restricted_data(job_id, training_data_path, data_lowest, data_highest)
    test_model(job_id, testing_data)


def ddl_based_best_configuration(job_id, deadline, data_size,
                                 machine_lowest, machine_highest, machine_interval, test_only):
    exp_file_name = job_id + ".csv"
    exp_data_path = os.path.join(DATA_PATH, exp_file_name)

    exp_dir = os.path.join(MODEL_PATH, job_id)
    training_data_path = os.path.join(exp_dir, exp_file_name)

    if not os.path.exists(training_data_path):
        create_experiment(exp_data_path, job_id, data_grouping=False)

    if not test_only:
        print training_data_path
        train_model(job_id, training_data_path)

    print training_data_path
    testing_data = generate_size_restricted_data(job_id, training_data_path, data_size,
                                                 machine_lowest, machine_highest, machine_interval)

    test_model(job_id, testing_data)

    return get_best_configuration(job_id, deadline)


def time_based_grouping(job_id):
    file_name = "predicted_candidates.csv"
    input_data_path = os.path.join(MODEL_PATH, job_id, file_name)

    gr = Grouping(data_file=input_data_path)
    scale_split = gr.time_based_grouping()

    # print scale_split
    return scale_split


if __name__ == '__main__':
    # time_based_grouping()
    job_id = "terasort"

    time_based_grouping(job_id)
    #
    # deadline = 1000
    # data_lowest = 1
    # data_highest = 50
    # data_interval = 1
    # machine_lowest = 4
    # machine_highest = 20
    # machine_interval = 4
    # #
    # # data_size = 7
    # #
    # data_grouping(job_id, data_lowest, data_highest, test_only=False)
    #
    # print ddl_based_best_configuration(job_id, deadline, data_size,
    #                                    machine_lowest, machine_highest, machine_interval, test_only=False)
