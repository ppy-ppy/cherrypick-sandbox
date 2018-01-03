import math

EXP_TYPE = "typeca"
EXPERIMENT = ['terasort','testdfsio','tpcds','spark','kmeans']
WEIGHT = [3,3,0,0,1]
GAMMA = 0.4
COST_FUNC = lambda cost: math.log(cost)
TIME_LIMIT = -1
