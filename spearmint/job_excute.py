from softmax_classifier import  softmax_classifier
from runtest import *
from path_config import *
import os
import multiprocessing
import time


job_id_to_weight_dict={"abc":[1,3,1,1,0]}

def job_id_to_weight(job_id):
    return job_id_to_weight_dict[job_id]

def job_io_cpu_feature(job_id,data_size):
    flag=True
    exp_name = job_id + "-" + data_size
    new_path = os.path.join(EXP_PATH, exp_name)
    if not os.path.exists(new_path):
        flag=False
        old_path = os.path.join(EXP_PATH, 'template')
        copy_tree(old_path, new_path)
        rename_exp(new_path, exp_name)
        replace_exp(old_path, new_path, "config.pb", exp_name)
        replace_exp(old_path, new_path, "experiment_config.py", exp_name)

    job_weight=job_id_to_weight(job_id)
    a,b=softmax_classifier(job_weight)
    if not flag:
        write_file = open(os.path.join(new_path, "experiment_config.py"), "r+")
        write_file.seek(0,2)
        write_file.write("WEIGHT = " + str(job_weight))
        write_file.close()
        flag=True

    #vm

    base_dir=os.path.abspath(os.path.dirname(__file__))
    print base_dir
    if not os.path.exists(base_dir+"/examples/"+exp_name+"/experiment.txt"):
        command_ = "python " + base_dir + "/spearmint/main.py  " + base_dir + "/examples/" + exp_name + "/config.pb"
        p = multiprocessing.Process(name="BO_process", target=os.system, args=(command_,))
        p.start()

    while not os.path.exists(base_dir+"/examples/"+exp_name+"/experiment.txt"):
        pass

    read_file = base_dir+"/examples/"+exp_name+"/experiment.txt"
    file_object = open(read_file, 'r')
    data = file_object.read()
    vm, cluster_size, exp_name = data.split(' ')
    return a,b,vm,int(cluster_size)  #a=(io_percentage,cpu_percentage)



def job_excute(job_id,data_size):
    exp_name = job_id + "-" + data_size
    base_dir = os.path.abspath(os.path.dirname(__file__))
    command_ = "python " + base_dir + "/examples/" + exp_name + "/offline.py"
    os.system(command_)

    while not os.path.exists(base_dir+"/examples/"+exp_name+"/total_time.txt"):
        pass

    read_file=open(base_dir+"/examples/"+exp_name+"/total_time.txt", "r")
    total_time=float(read_file.read())
    print(total_time)
    os.system("rm -f "+base_dir+"/examples/"+exp_name+"/total_time.txt")
    return total_time


if __name__ == '__main__':
    #print(job_io_cpu_feature("abc","2"))   #percentile
    #os.system("python ./examples/abc-2/experiment_config.py")
    #while True:
    job_excute("abc","2")
    #os.system("python " +base_dir+"/examples/abc-2/offline.py")

