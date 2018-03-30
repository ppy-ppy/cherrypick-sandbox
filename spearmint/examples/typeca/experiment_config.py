import math

EXP_TYPE = "typeca"
EXPERIMENT = ['terasort','testdfsio','tpcds','spark','kmeans']
WEIGHT = [9,9,0,1,1]
GAMMA = 0.4
COST_FUNC = lambda cost: math.log(cost)
TIME_LIMIT = -1
