import math

EXP_TYPE = "typeba"
EXPERIMENT = ['terasort','testdfsio','tpcds','spark','kmeans']
WEIGHT = [1,1,1,0,0]
GAMMA = 0.4
COST_FUNC = lambda cost: math.log(cost)
TIME_LIMIT = -1