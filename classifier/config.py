import xlrd
import os

CLASSIFIER_PATH = os.path.abspath(os.path.dirname(__file__))

data = xlrd.open_workbook(os.path.join(CLASSIFIER_PATH, 'result.xlsx'))
parameter_output = os.path.join(CLASSIFIER_PATH, 'parameters.py')

labels = [[0.2, 0.8], [0.3, 0.7], [0.4, 0.6], [0.5, 0.5], [0.6, 0.4]]  # label_0:io   label_1:cpu

meta_jobs = ['terasort', 'testdfsio', 'tpcds', 'spark', 'kmeans']

io_measure_index = [2, 4, 5]
cpu_measure_index = [5, 3, 1]
