import os
import shutil
# import model_built
# from test123 import model_built


FILE_PATH = os.path.abspath(os.path.dirname(__file__))


def get_configuration(job_id):
    exp_dir = os.path.join(FILE_PATH, job_id)
    if not os.path.exists(exp_dir):
        os.mkdir(exp_dir)
        init_file = os.path.join(exp_dir, '__init__.py')
        open(init_file, 'w')

        src_file = os.path.join(FILE_PATH, "model_built.py")
        dst_file = os.path.join(exp_dir, "model_built.py")
        shutil.copy(src_file, dst_file)

        src_file = os.path.join(FILE_PATH, "experiment_data.csv")
        dst_file = os.path.join(exp_dir, "experiment_data.csv")
        shutil.copy(src_file, dst_file)

    # print job_id

    mod = __import__(job_id,
                     fromlist=['model_built', ])
    model_built = mod.model_built
    model_built.train_data()
    model_built.generate_data()
    model_built.test_data()

    # compare_data = model_built.read_training_data("compare.csv")
    print model_built.ddl_get_lowest_cost()


if __name__ == '__main__':
    get_configuration("test000")
