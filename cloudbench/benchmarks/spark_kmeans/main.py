from cloudbench.ssh import WaitUntilFinished, WaitForSeconds
from cloudbench.util import Debug, parallel
from cloudbench.cloudera.cloudera import Cloudera
from cloudbench.cluster.base import Cluster
from cloudbench.util import Config

import os
import re
import time

def makedirectory(name):
    if not os.path.exists(name):
        os.makedirs(name)

def argos_start(vms):
    parallel(lambda vm: vm.script('rm -rf ~/argos/proc'), vms)
    parallel(lambda vm: vm.script('cd argos; sudo nohup src/argos >argos.out 2>&1 &'), vms)
    time.sleep(2)

def argos_finish(vms, directory, iteration):
    parallel(lambda vm: vm.script('sudo killall -SIGINT argos'), vms)
    time.sleep(30)
    parallel(lambda vm: vm.script('chmod -R 777 ~/argos/proc'), vms)

    # Delete empty files
    parallel(lambda vm: vm.script('find ~/argos/proc -type f -empty -delete'), vms)
    # Delete empty directories
    parallel(lambda vm: vm.script('find ~/argos/proc -type d -empty -delete'), vms)

    subdir=os.path.join(directory, str(iteration))
    makedirectory(subdir)

    # Save argos results
    parallel(lambda vm: vm.recv('~/argos/proc', os.path.join(subdir, vm.name + '-proc')), vms)

    # Save argos output
    parallel(lambda vm: vm.recv('~/argos/argos.out', os.path.join(subdir, vm.name + '-argos.out')), vms)


def setup_hadoop(env, vms):
    setup_base(env, vms)
    ce = Cloudera(vms)
    ce.install('Hadoop')
    return ce['Hadoop']

def setup_base(env, vms):
    parallel(lambda vm: vm.install('java8'), vms)
    parallel(lambda vm: vm.install('cloudera'), vms)
    parallel(lambda vm: vm.install('git'), vms)
    parallel(lambda vm: vm.install('argos'), vms)

def setup_spark(env, vms):
    setup_base(env, vms)
    ce = Cloudera(vms)
    ce.install('Hadoop')
    ce.install('Spark')
    return ce['Spark']

def run_spark(vms, env):
    # install the spark-perf
    # update the config.py file ... mark mllib stuff as on
        # OptionSet("num-partitions", [128], can_scale=True) -- set 128 to the number of cores in the cluster
    # etc. etc.

    # Setup ssh keys
    # cluster = Cluster(vms, user='ubuntu')
    # cluster.setup_keys()

    # Setup disks
    # setup_disks(env, vms)
    #
    # # Setup spark
    master_vm = None
    for vm in vms:
        if vm.name == 'master':
            master_vm = vm
            break
    path = Config.path('tools', 'login.sh')
    master_vm.send(path, '/home/ubuntu')
    master_vm.script('sudo chmod 777 /home/ubuntu/login.sh')
    master_vm.script('cd /home/ubuntu; ./login.sh')
    path = Config.path('tools', 'json4s-jackson_2.11-3.2.10.jar')
    master_vm.send(path, '/home/ubuntu')
    path = Config.path('tools', 'spark-core_2.11-1.5.2.jar')
    master_vm.send(path, '/home/ubuntu')
    master_vm.script('sudo mv /home/ubuntu/json4s-jackson_2.11-3.2.10.jar /opt/spark/jars')
    master_vm.script('sudo mv /home/ubuntu/spark-core_2.11-1.5.2.jar /opt/spark/jars')
    master_vm.script('sudo mv /opt/spark/jars/json4s-jackson_2.11-3.2.11.jar /home/ubuntu/')
    parallel(lambda vm: vm.script("sync; echo 3 > /proc/sys/vm/drop_caches"), vms)
    setup_spark_kmeans(env, vms)

    dir_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    cloudbench_path = os.path.abspath(os.path.dirname(os.path.dirname(dir_path)))
    result_path = os.path.join(cloudbench_path, "results")
    result_name = 'kmeans-' + vm._config['type'] + '-' + str(len(vms)) + "-results"
    directory = os.path.join(result_path, result_name)
    makedirectory(directory)
    iteration = str(1)

    subdir = os.path.join(directory, str(iteration))
    makedirectory(subdir)
    master_vm.script('sudo mv /home/ubuntu/spark-perf-kmeans /home/hadoop/')
    master_vm.script('sudo chown -R hadoop:hadoop /home/hadoop/spark-perf-kmeans')
    master_vm.script('sudo touch /home/hadoop/spark-perf-kmeans/bin/results/time')
    master_vm.script('sudo chmod 777 /home/hadoop/spark-perf-kmeans/bin/results/time')
    master_vm.script('sudo su hadoop -l -c "cd /home/hadoop/spark-perf-kmeans/bin; ./run > /home/hadoop/spark-perf-kmeans/bin/output.log 2>&1"')
    kmeans_time = master_vm.script('cd /home/hadoop/spark-perf-kmeans; tail -n1 /home/hadoop/spark-perf-kmeans/bin/results/time').strip()
    kmeans_out = master_vm.script('cat /home/hadoop/spark-perf-kmeans/bin/output.log').strip()
    file_name = master_vm.type
    with open(os.path.join(directory, str(iteration), file_name + ".time"), 'w+') as f:
        f.write("0," + str(kmeans_time))

    with open(os.path.join(directory, str(iteration), file_name + ".out"), 'w+') as f:
        f.write(kmeans_out)
    master_vm.script('sudo mv /opt/spark/jars/json4s-jackson_2.11-3.2.10.jar /home/ubuntu/')

    #master_vm.script('sudo mv /home/ubuntu/spark-perf-kmeans/json4s-jackson_2.11-3.2.11.jar /opt/spark/jars')
    master_vm.script('sudo mv /home/ubuntu/json4s-jackson_2.11-3.2.11.jar /opt/spark/jars')
    master_vm.script('sudo mv /opt/spark/jars/spark-core_2.11-1.5.2.jar /home/ubuntu/')


    # Setup spark perf

    # directory='spark-' + spark.master.type + '-' + str(len(vms)) + "-results"
    # makedirectory(directory)
    # iteration=str(1)


    # Make sure spark can be written by anyone
    # parallel(lambda vm: vm.script('chown -R ubuntu:ubuntu /var/lib/spark/work'), vms)
    # parallel(lambda vm: vm.script('sudo -u hdfs hdfs dfs -chmod 777 /user/spark'), vms)
    #
    # argos_start(vms)
    # spark.master.script('cd /home/ubuntu/spark-perf-kmeans; ./bin/run >log.out 2>&1')
    # argos_finish(vms, directory, iteration)
    #
    # spark_time = spark.master.script('cd /home/ubuntu/spark-perf-kmeans; tail -n1 out.time').strip()
    # spark_out = spark.master.script('cd /home/ubuntu/spark-perf-kmeans; cat log.out').strip()
    # file_name = spark.master.type
    # with open(os.path.join(directory, str(iteration), file_name + ".time"), 'w+') as f:
    #     f.write("0," + str(spark_time))
    #
    # with open(os.path.join(directory, str(iteration), file_name + ".out"), 'w+') as f:
    #     f.write(spark_out)

def spark_driver_memory(vm):
    ram_mb = int(vm.memory() / (1024*1024))
    ret = ram_mb
    if ram_mb > 100*1024:
        ret =  ram_mb - 15 * 1024
    elif ram_mb > 60*1024:
        ret =  ram_mb - 10 * 1024
    elif ram_mb > 40*1024:
        ret =  ram_mb - 6 * 1024
    elif ram_mb > 20*1024:
        ret =  ram_mb - 3 * 1024
    elif ram_mb > 10*1024:
        ret =  ram_mb - 2 * 1024
    else:
        ret =  max(512, ram_mb - 1300)

    ret -= max(400, ret*0.2)

    return int(ret)

def setup_spark_kmeans(env, vms):
    path = Config.path('tools', 'spark-perf-kmeans.tar.gz')
    parallel(lambda vm: vm.send(path, '/home/ubuntu'), vms)
    parallel(lambda vm: vm.script('rm -rf /home/ubuntu/spark-perf-kmeans'), vms)
    parallel(lambda vm: vm.script('tar -xzf spark-perf-kmeans.tar.gz'), vms)
    num_cores = len(vms) * vms[0].cpus()

    def replace_line(vm):
        vm.script("cd spark-perf-kmeans; sed -i '/OptionSet(\"num-partitions\", \[128\], can_scale=True),/c\    OptionSet(\"num-partitions\", [%d], can_scale=False),' config/config.py" % num_cores )
        vm.script("cd spark-perf-kmeans; sed -i '/OptionSet(\"num-trials\", \[10\]),/c\    OptionSet(\"num-trials\", \[5\]),' config/config.py" )
        vm.script("cd spark-perf-kmeans; sed -i '/SPARK_DRIVER_MEMORY = \"5g\"/c\SPARK_DRIVER_MEMORY = \"%dm\"' config/config.py" % spark_driver_memory(vm))
        vm.script("cd spark-perf-kmeans; sed -i '/JavaOptionSet(\"spark.storage.memoryFraction\", \[0.66\]),/c\    JavaOptionSet(\"spark.storage.memoryFraction\", \[0.66\]), JavaOptionSet(\"spark.yarn.executor.memoryOverhead\", \[500\]),' config/config.py")
        vm.script("cd spark-perf-kmeans; sed -i '/OptionSet(\"num-examples\", \[100000\], can_scale=False)/c\    OptionSet(\"num-examples\", \[%d\], can_scale=False),' config/config.py" % int('100000'))    #env.param('sparkml:examples')
    parallel(replace_line, vms)

def setup_disks(env, vms):
    def setup_vm_disks(vm):
        root = vm.root_disk()
        disks = vm.disks()
        disk_id = 2

        if len(disks) == 0:
            disks = vm.local_disks_except_root()

        for disk in disks:
            if root.startswith(disk):
                continue
            vm.mount(disk, '/data/%d' % disk_id, force_format=True)
            vm.script("chmod 777 -R /data/%d" % disk_id)
            disk_id += 1
    parallel(setup_vm_disks, vms)

def run(env):
    vms = env.virtual_machines().values()
    env.benchmark.executor(vms, run_spark)
    env.benchmark.executor.run()
