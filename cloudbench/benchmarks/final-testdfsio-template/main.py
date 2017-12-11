from cloudbench.ssh import WaitUntilFinished, WaitForSeconds
from cloudbench.util import Debug, parallel
from cloudbench.benchmarks.testdfsio_cloudera import testdfsio

import re
import time

TIMEOUT=21600

def run(env):
    vms = env.virtual_machines().values()
    env.benchmark.executor(vms, testdfsio)
    env.benchmark.executor.run()
