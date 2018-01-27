#coding: utf-8


import shutil
from path_config import *
import re


def clean_path(path):
    path = path.strip()
    path = path.rstrip("\\")

    return path


def mkdir(path):
    path = clean_path(path)

    isExists = os.path.exists(path)

    if not isExists:
        os.makedirs(path)
        print path + ' is created successfully!'
        return True
    else:
        print path + ' already exists!'
        return False


def copy_tree(old_path, new_path):
    old_path = clean_path(old_path)
    new_path = clean_path(new_path)

    if not os.path.exists(old_path):
        print old_path + ' does not exist!'
        return False

    if os.path.exists(new_path):
        print new_path + ' already exists!'
        return False

    shutil.copytree(old_path, new_path)
    return True


def replace_exp(old_path, new_path, file_name, exp_name):
    read_file = open(os.path.join(old_path, file_name), "r")
    write_file = open(os.path.join(new_path, file_name), "w")

    key = "template"
    for line in read_file.readlines():
        new_line = re.sub(key, exp_name, line)
        write_file.write(new_line)


def rename_exp(path, exp_name):
    template_name = os.path.join(path, "template.py")
    dst_name = os.path.join(path, exp_name + ".py")
    os.rename(template_name, dst_name)


if __name__ == '__main__':
    job_id = "abc"
    data_size = "1"
    exp_name = job_id + "-" + data_size
    old_path = os.path.join(EXP_PATH, 'template')
    new_path = os.path.join(EXP_PATH, exp_name)
    print BO_PATH
    print old_path
    print new_path
    copy_tree(old_path, new_path)
    rename_exp(new_path, exp_name)
    # mkdir(new_path)
    replace_exp(old_path, new_path, "config.pb", exp_name)
    replace_exp(old_path, new_path, "experiment_config.py", exp_name)
