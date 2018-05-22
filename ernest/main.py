import os
import shutil


FILE_PATH = os.path.abspath(os.path.dirname(__file__))
MODEL_PATH = os.path.join(FILE_PATH, "models")


def create_experiment(exp_data_path, job_id):
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

        src_file = os.path.join(exp_data_path)
        dst_file = os.path.join(exp_dir, "experiment_data.csv")
        shutil.copy(src_file, dst_file)


def train_model(job_id):
    mod = __import__("models." + job_id,
                     fromlist=['model_built', ])
    model_built = mod.model_built
    input_path = model_built.INPUT_PATH
    training_data = model_built.read_training_data(input_path)
    model_built.train_data(training_data)


def generate_arbitrary_data(job_id, lowest, highest, interval, machine_lowest, machine_highest, machine_interval):
    mod = __import__("models." + job_id,
                     fromlist=['model_built', ])
    model_built = mod.model_built
    model_built.generate_testing_data(lowest, highest, interval, machine_lowest, machine_highest, machine_interval)

    test_path = model_built.TEST_PATH
    testing_data = model_built.read_file(test_path)
    return testing_data


def generate_machine_restricted_data(job_id, lowest, highest):
    mod = __import__("models." + job_id,
                     fromlist=['data_grouping', 'model_built', ])
    data_grouping = mod.data_grouping
    model_built = mod.model_built
    data_grouping.generate_testing_data(lowest, highest)

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


if __name__ == '__main__':
    job_id = "test006"
    exp_data_path = os.path.join(FILE_PATH, "data_grouping_input.csv")
    # exp_data_path = os.path.join(FILE_PATH, "experiment_data.csv")
    deadline = 60
    lowest = 1
    highest = 100
    interval = 1
    machine_lowest = 2
    machine_highest = 18
    machine_interval = 2

    create_experiment(exp_data_path, job_id)
    train_model(job_id)
    # testing_data = \
    #     generate_arbitrary_data(job_id, lowest, highest, interval, machine_lowest, machine_highest, machine_interval)
    testing_data = generate_machine_restricted_data(job_id, lowest, highest)
    test_model(job_id, testing_data)
    print get_best_configuration(job_id, deadline)
