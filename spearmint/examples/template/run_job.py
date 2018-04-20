import re
from env_config import *


def run_job(vm, cluster_size, exp_name):
    dir_name = exp_name + '-' + vm + '-' + str(cluster_size) + "-results"
    path = os.path.join(RESULT_PATH, dir_name)
    if os.path.exists(path):
        cmd = "rm -rf " + path
        print cmd
        print os.system(cmd)

    command = EXE_PATH + "/execute.sh 0 " + exp_name + " " + vm + " " + str(cluster_size)
    print command
    print os.system(command)

    while os.path.exists(path) is False:
        continue

    logfile = path + '/1/' + vm + '.out'
    fp = open(logfile, "r")

    if exp_name == "terasort" or exp_name == "testdfsio":
        keyword = "completed successfully"
    elif exp_name == "tpcds":
        keyword = "<b>Failures:</b> 0"
    elif exp_name == "kmeans" or exp_name == "spark":
        keyword = "Number of failed tests: 0"

    success = 0
    for s in fp.readlines():
        success += len(re.findall(keyword, s))

    fp.close()
    print success
    if success == 0:
        return -1

    filename = path + '/1/' + vm + '.time'
    f = open(filename)
    line = f.readline()
    run_time = float(line.split(',')[1])

    print "run time is :", run_time
    return run_time