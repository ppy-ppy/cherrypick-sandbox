from cloudbench.ssh import WaitUntilFinished, WaitForSeconds
from cloudbench.util import Debug, parallel
from cloudbench.cloudera.cloudera import Cloudera
from cloudbench.apps.spark_sql_perf import SPARK_SQL_PERF_DIR
from cloudbench.apps.spark_sql_perf import install as install_spark_sql_perf

import os
import random
import re
import time

TIMEOUT=21600

TPCDS_SCALE=3
GenerateTPCDS = """
import com.databricks.spark.sql.perf.tpcds.Tables

val sqlContext = new org.apache.spark.sql.SQLContext(sc)
val dsdgenDir = "/home/ubuntu/tpcds-kit/tools"
val dbName = "tpcdsdb_lb"
val scaleFactor = {scaleFactor}
val tables = new Tables(sqlContext, dsdgenDir, scaleFactor)
val location = "/user/spark/tpcds"
val format = "parquet"

tables.genData(location, format, true, true, true, true, true)
tables.createExternalTables(location, format, dbName, true)
:quit
"""

ExecuteTPCDS = """
import com.databricks.spark.sql.perf.tpcds.TPCDS

val sqlContext = new org.apache.spark.sql.SQLContext(sc)
val dbName = "tpcdsdb_lb"
sqlContext.sql("USE tpcdsdb_lb")
sc.setLogLevel("WARN")
val tpcds = new TPCDS()
val expt = tpcds.runExperiment(tpcds.cherryPickQueries)
expt.waitForFinish(10000)

expt.html
:quit
"""
# cherryPickQueries
def argos_start(vms, directory, iteration):
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


def setup_base(vms, env):
    parallel(lambda vm: vm.install('java8'), vms)
    parallel(lambda vm: vm.install('argos'), vms)
    parallel(lambda vm: vm.install('cloudera'), vms)
    parallel(lambda vm: vm.install('tpcds_kit'), vms)
    parallel(lambda vm: vm.install('spark_sql_perf'), vms)

def setup_spark(vms, env):
    setup_disks(vms, env)
    setup_base(vms, env)

    ce = Cloudera(vms)
    ce.install('Hadoop')
    ce.install('Spark')

    # Make sure spark can be written by anyone
    parallel(lambda vm: vm.script('chown -R ubuntu:ubuntu /var/lib/spark/work'), vms)
    parallel(lambda vm: vm.script('sudo -u hdfs hdfs dfs -chmod 777 /user/spark'), vms)

    return ce['Spark']

def setup_disks(vms, env):
    def setup_vm_disks(vm):
        vm.script('rm -rf /data/1/')
        root = vm.root_disk()
        disks = vm.disks()
        disk_id = 2

        if len(disks) == 0 or vm.type == 'i2.8xlarge':
            disks = vm.local_disks_except_root()

        for disk in disks:
            if root.startswith(disk):
                continue
            vm.mount(disk, '/data/%d' % disk_id, force_format=True)
            disk_id += 1
    parallel(setup_vm_disks, vms)


def makedirectory(name):
    if not os.path.exists(name):
        os.makedirs(name)

def spark_executor_memory(vm):
    return int(spark_driver_memory(vm) / (2*vm.cpus()))

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

def tpcds(vms, env):
    # spark = setup_spark(vms, env)
    def prepare_spark(vm):
        vm.script('chown -R ubuntu:ubuntu %s' % SPARK_SQL_PERF_DIR)
        # vm.script('cd %s; sudo -u ubuntu ./build/sbt package' % SPARK_SQL_PERF_DIR)

    def write_file(vm, fName, content):
        vm.script("sudo cat <<EOT > {0}\n{1}\nEOT".format(fName, content))

    genFile = os.path.join(SPARK_SQL_PERF_DIR, "gen.cmd")
    exeFile = os.path.join(SPARK_SQL_PERF_DIR, "exe.cmd")

    #
    def load_tpcds_scripts(vm):
        write_file(vm, genFile, GenerateTPCDS.format(scaleFactor=TPCDS_SCALE))
        write_file(vm, exeFile, ExecuteTPCDS)

    #
    def exec_tpcds_script(master, slave, script, output, extra=""):
        # cmdTpl = "sudo su hadoop -l -c '/opt/spark/bin/spark-shell --jars {0} --conf spark.driver.memory={1}m -i {2} --conf spark.executor.memory={4}m {5} |& tee {3}'"
        # cmd = cmdTpl.format(os.path.join(SPARK_SQL_PERF_DIR,
        #     "target", "scala-2.11", "spark-sql-perf_2.11-0.4.3.jar"),
        #     spark_driver_memory(master),
        #     script, output, spark_executor_memory(slave), extra)
        cmdTpl = "sudo su hadoop -l -c '/opt/spark/bin/spark-shell --jars {0} -i {1} |& tee {2}'"
        cmd = cmdTpl.format(os.path.join(SPARK_SQL_PERF_DIR,
                                         "target", "scala-2.11", "spark-sql-perf_2.11-0.4.3.jar"),
                            script, output )
        master.script(cmd)

    # For some reason the Namenode was failing here ...
    # TODO: debug here ...
    master_vm = None
    slave_vm = None
    for vm in vms:
        if vm.name == 'master':
            master_vm = vm
        if vm.name == 'slave-0':
            slave_vm = vm
    master_vm.script('sudo rm -rf /home/ubuntu/spark-sql-perf')
    master_vm.script('sudo rm -rf /home/ubuntu/spark-sql-perf.tar.gz')
    master_vm.script('sudo su hadoop -l -c "rm -rf /home/hadoop/spark-sql-perf"')
    parallel(lambda vm: vm.script("sync; echo 3 > /proc/sys/vm/drop_caches"), vms)
    # spark.master.script("sudo service hadoop-hdfs-namenode restart")
    # spark.master.script("sudo service hadoop-yarn-resourcemanager restart")
    master_vm.script("sudo -u hdfs hdfs dfs -mkdir -p /user/spark")

    install_spark_sql_perf(master_vm)

    # Make hdfs read/write/executable by anyone
    master_vm.script("sudo -u hdfs hdfs dfs chmod -R 777 /")

    # prepare spark
    parallel(prepare_spark, vms)

    # Save the TPC-DS scripts to remote virtual machines
    parallel(load_tpcds_scripts, vms)

    dir_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    cloudbench_path = os.path.abspath(os.path.dirname(os.path.dirname(dir_path)))
    result_path = os.path.join(cloudbench_path, "results")
    result_name = 'tpcds-' + master_vm._config['type'] + '-' + str(len(vms)) + "-results"
    directory = os.path.join(result_path, result_name)
    makedirectory(directory)
    iteration=str(1)

    subdir = os.path.join(directory, str(iteration))
    makedirectory(subdir)

    # execute scripts
    ## Generate TPCDS data
    exec_tpcds_script(master_vm, slave_vm, genFile, os.path.join(SPARK_SQL_PERF_DIR, "gen.log"), "--conf spark.yarn.executor.memoryOverhead=768")
    # os.path.join(SPARK_SQL_PERF_DIR, "gen.log")
    parallel(lambda vm: vm.script("sync; echo 3 > /proc/sys/vm/drop_caches"), vms)
    ## Execute TPCDS queries
    # argos_start(vms, directory, iteration)
    start = time.time()
    exec_tpcds_script(master_vm, slave_vm, exeFile, os.path.join(SPARK_SQL_PERF_DIR, "exe.log"))
    end = time.time()
    # argos_finish(vms, directory, iteration)

    file_name = master_vm._config['type']
    with open(os.path.join(directory, str(iteration), master_vm._config['type'] + '.time'), 'w+') as f:
        f.write('0,%s' % str(end - start))

    file_name = master_vm.type
    master_vm.recv("/home/ubuntu/spark-sql-perf/gen.log", os.path.join(directory, str(iteration), "gen.log"))
    master_vm.recv("/home/ubuntu/spark-sql-perf/exe.log", os.path.join(directory, str(iteration), file_name + ".out"))


def run(env):
    vms = env.virtual_machines().values()
    env.benchmark.executor(vms, tpcds)
    env.benchmark.executor.run()
