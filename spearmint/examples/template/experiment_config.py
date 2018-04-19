import math

# TODO: EXP_TYPE = JOB_ID + DATA_SIZE
EXP_TYPE = "template"
EXPERIMENT = ['terasort', 'testdfsio', 'tpcds', 'spark', 'kmeans']
# TODO: receive parameters for weight
# WEIGHT = [8, 1, 1, 1, 1]
GAMMA = 0.4
COST_FUNC = lambda cost: math.log(cost)
TIME_LIMIT = -1
