import math

EXP_TYPE = "typeaa"
EXPERIMENT = ['kmeans', 'terasort', 'tpcds', 'testdfsio', 'spark']
WEIGHT = [0, 2, 1, 0, 0]
GAMMA = 0.4
COST_FUNC = lambda cost: math.log(cost * 100)
TIME_LIMIT = -1

