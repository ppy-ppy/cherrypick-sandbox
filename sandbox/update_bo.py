from env_config import *
from ernest.output_data import *
from spearmint.schema import JobInfo
from sandbox.experiment import Experiment


def find_and_update_run(vm, cluster_size, user_id, job_id, time, scale):
    experiment = Experiment(job_id, user_id, scale)
    job = JobInfo.find_job_info(experiment.job_id, experiment.user_id)
    runs = job.find_runs(vm, int(cluster_size))

    if float(time) != -1:
        runs[0].time = runs[0].time * GAMMA + (1 - GAMMA) * float(time)
        runs[0].num = 1
        # print vm
    # print runs
    output_test_time_ernest(vm, int(cluster_size), experiment.name, float(time), str(scale))
    return runs[0]