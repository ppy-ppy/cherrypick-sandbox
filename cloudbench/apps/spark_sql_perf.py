from cloudbench.util import Config

SPARK_SQL_PERF_PATH='/home/ubuntu/'
SPARK_SQL_PERF_DIR='%s/spark-sql-perf' % SPARK_SQL_PERF_PATH 
SPARK_SQL_PERF_FILE='spark-sql-perf.tar.gz'

def install(vm):
    vm.script("rm -rf %s" % SPARK_SQL_PERF_DIR);
    vm.send(Config.path('tools', SPARK_SQL_PERF_FILE), SPARK_SQL_PERF_PATH)
    vm.cd(SPARK_SQL_PERF_PATH).execute('tar xzf {0}'.format(SPARK_SQL_PERF_FILE));
    vm.script("rm -rf /home/ubuntu/tpcds-kit.tar.gz");
    vm.script("rm -rf /home/ubuntu/tpcds-kit");
    vm.send(Config.path('tools', 'tpcds-kit.tar.gz'), SPARK_SQL_PERF_PATH)
    vm.cd('~/').execute('tar xzf {0}'.format('tpcds-kit.tar.gz'));
    vm.script("sudo chmod -R 777 /home/ubuntu/spark-sql-perf");
    vm.script("sudo chmod -R 777 /home/ubuntu/tpcds-kit");

def remove(vm):
    vm.rmdir(SPARK_SQL_PERF_DIR)

def installed(vm):
    return vm.isdir(SPARK_SQL_PERF_DIR)

