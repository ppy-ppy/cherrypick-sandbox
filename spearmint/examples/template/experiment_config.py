import math
import os

# TODO: EXP_TYPE = JOB_ID + DATA_SIZE
EXP_PATH = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
EXP_TYPE = "template"
EXPERIMENT = ['terasort', 'testdfsio', 'tpcds', 'spark', 'kmeans']
# TODO: receive parameters for weight
# WEIGHT = [8, 1, 1, 1, 1]

COST_FUNC = lambda cost: math.log(cost)
TIME_LIMIT = -1

flavor_space = [
    "m1.medium",
    "m1.large",
    "m1.xlarge",
    "r2.small",
    "r2.medium",
    "r2.large",
    "r2.xlarge",
    "c3.medium",
    "c3.large",
    "c3.xlarge"
]

machine_space = [2, 4, 8, 16]