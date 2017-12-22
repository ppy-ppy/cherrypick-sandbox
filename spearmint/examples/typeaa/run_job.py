import os
import re


def run_job(vm, cluster_size, exp_name):
    dirname = exp_name + '-' + vm + '-' + str(cluster_size) + "-results"
    if os.path.exists(dirname):
        cmd = "rm -rf " + dirname
        print cmd
        print os.system(cmd)

    command = "./run.sh 0 " + exp_name + " " + vm + " " + str(cluster_size)
    print command
    print os.system(command)

    while os.path.exists(dirname) is False:
        continue

    logfile = dirname + '/1/' + vm + '.out'
    fp = open(logfile, "r")
    errors = 0
    for s in fp.readlines():
        errors += len(re.findall("ERROR", s))
        errors += len(re.findall("failed", s))

    fp.close()
    print errors
    if errors > 0:
        return -1

    filename = dirname + '/1/' + vm + '.time'
    f = open(filename)
    line = f.readline()
    run_time = float(line.split(',')[1])

    print "run time is :", run_time
    return run_time