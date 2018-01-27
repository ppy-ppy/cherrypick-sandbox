import math

EXP_TYPE = "typeda"
EXPERIMENT = ['terasort','testdfsio','tpcds','spark','kmeans']
WEIGHT = [1,9,0,0,0]
GAMMA = 0.4
COST_FUNC = lambda cost: math.log(cost)
TIME_LIMIT = -1
