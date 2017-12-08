import os
import random


def makedirectory(name):
    if not os.path.exists(name):
        os.makedirs(name)


def local(vms, env):
    spark_master_type = 'local_type'
    directory='local-' + spark_master_type + '-' + str(len(vms)) + "-results"
    makedirectory(directory)
    iteration = str(1)
    makedirectory(directory + '/' + iteration)

    run_time = random.uniform(300, 1000)
    spark_out = spark_master_type
    file_name = spark_master_type

    with open(os.path.join(directory, str(iteration), spark_master_type + '.time'), 'w+') as f:
        f.write('0,%s' % str(run_time))
    with open(os.path.join(directory, str(iteration), file_name + ".out"), 'w+') as f:
        f.write(spark_out)


def run(env):
    vms = env.virtual_machines().values()
    env.benchmark.executor(vms, local)
    env.benchmark.executor.run()
