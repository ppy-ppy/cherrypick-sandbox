import os


def run_job(vm, cluster_size, exp_name):
    command = "./run.sh 0 " + exp_name + " " + vm + " " + str(cluster_size)
    print command
    print os.system(command)

    dirname = exp_name + '-' + vm + '-' + str(cluster_size) + "-results"
    while os.path.exists(dirname) is False:
        continue
    filename = dirname + '/1/' + vm + '.time'
    f = open(filename)
    line = f.readline()
    run_time = float(line.split(',')[1])

    print "run time is :", run_time
    return run_time