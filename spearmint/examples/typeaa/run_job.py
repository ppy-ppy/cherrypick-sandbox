import os
import re


def run_job(vm, cluster_size, exp_name):
    dirname = exp_name + '-' + vm + '-' + str(cluster_size) + "-results"
    if os.path.exists(dirname):
        cmd = "rm -rf " + dirname
        print cmd
        print os.system(cmd)

    command = "./execute.sh 0 " + exp_name + " " + vm + " " + str(cluster_size)
    print command
    print os.system(command)

    while os.path.exists(dirname) is False:
        continue

    logfile = dirname + '/1/' + vm + '.out'
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

    filename = dirname + '/1/' + vm + '.time'
    f = open(filename)
    line = f.readline()
    run_time = float(line.split(',')[1])

    print "run time is :", run_time
    return run_time