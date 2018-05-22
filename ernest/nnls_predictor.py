import numpy as np
import scipy
from scipy.optimize import nnls
import csv
import sys
import os
import math
from sqlobject import *
from spearmint.schema import VirtualMachineType as VM
from sandbox.openstack_api import *


FILE_PATH = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(FILE_PATH, "lowest.csv")
INPUT_PATH = os.path.join(FILE_PATH, "experiment_data.csv")
deadline = 60


class Nnls_Predictor(object):
    def __init__(self, name, training_data_in=[], data_file=None):
        '''
            Initiliaze the Predictor with some training data
            The training data should be a list of [mcs, input_fraction, time]
        '''
        self.training_data = []
        self.name = name

        if data_file:
            with open(data_file, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ')
                for row in reader:
                    if row[0][0] != '#':
                        parts = row[0].split(',')
                        vm_type = str(parts[3])
                        # cpus = int(parts[2])
                        # ram = float(parts[3])
                        mc = int(parts[0])
                        scale = float(parts[1])
                        time = float(parts[2])
                        self.training_data.append([mc, scale, time, vm_type])



    # def create_son_csv_file(self, vm_name_list_all):
    #     vm_name_list_all= self.vm_name_list()
    #     for i in vm_name_list_all:
    #         csv_new_name = vm_name_list_all[i]
    #         file = csv_new_name + ".csv"
    #         with open(file, "w") as csvfile:
    #             writer = csv.writer(csvfile)
    #             writer.writerow(["mc", "scale", "time", "vm_type"])
    #             for row in self.training_data:
    #                 if row[5] == csv_new_name:
    #                     writer.writerow([row[0], row[3], row[4], row[5]])
    #     return None


    # def create_data_group(self, data_file):
    #     training_data_group = []
    #     if data_file:
    #         with open(data_file, 'rb') as csvfile:
    #             reader = csv.reader(csvfile)
    #         for row in reader:
    #             if row[0] != "mc":
    #                 training_data_group.append(row)
    #     return training_data_grou

    def _get_features(self, training_point):
        # print 4
        mc = training_point[0]
        scale = training_point[1]

        return [1.0, float(scale) / float(mc), float(mc), np.log(mc)]


    def predict(self, mcs, input_fraction):
        # print 1
        '''
            Predict running time for given input fraction, number of machines.
        '''
        test_features = np.array(self._get_features([mcs, input_fraction]))
        return test_features.dot(self.model[0])


    def predict_all(self, test_data):
        '''
            Predict running time for a batch of input sizes, machines.
            Input test_data should be a list where every element is (input_fraction, machines)
        '''
        test_features = np.array([self._get_features([row[0], row[1]]) for row in test_data])
        return test_features.dot(self.model[0])

    def fit(self, training_point):
        print "Fitting a model with ", len(training_point), " points"
        labels = np.array([row[2] for row in training_point])
        data_points = np.array([self._get_features(row) for row in training_point])
        # print "fit"
        self.model = nnls(data_points, labels)
        # TODO: Add a debug logging mode ?
        training_errors = []
        for p in training_point:
            predicted = self.predict(p[0], p[1])
            training_errors.append(predicted / p[2])

            # print "#######"
            # print predicted
        print "Average training error %f%%" % ((np.mean(training_errors) - 1.0) * 100.0)
        return self.model[0]

    def train_data(self):
        # print self.training_data
        return self.training_data




# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print "Usage <predictor.py> <csv_file_train>"
#         sys.exit(0)
#
#     predictor_data = []
#
#     pred = Pure_Predictor(data_file=sys.argv[1])
#
#     train_data_list = pred.train_data()#xunlian shuju
#
#     vm_name_list_all = pred.vm_name_list()#shengcheng shuju flavor
#
#     predicted_times_all = []
#
#     compare_data = []
#
#     for i in vm_name_list_all:
#         file_name = vm_name_list_all[i] + ".csv"
#         training_point = []
#         with open(file_name, "w") as csvfile:
#             writer = csv.writer(csvfile)
#             writer.writerow(["mc", "scale", "time", "vm_type"])
#             for row in train_data_list:
#                 if row[5] == vm_name_list_all[i]:
#                     writer.writerow([row[0], row[3], row[4], row[5]])
#                     training_point.append([row[0], row[3], row[4], row[5]])
#
#         model = pred.fit(training_point)
#
#         test_data = []
#
#         for j in range(2, 16, 2):#i  is  mcs
#             for k in xrange(1,10):#j  is  scale
#                 if (j == 4) or (j == 8) or (j == 16) or (j==2):
#                     test_data.append([j, k, vm_name_list_all[i]])
#
#         predicted_times = np.ndarray.tolist(pred.predict_all(test_data))
#
#         for j in range(len(test_data)):
#             compare_data.append([test_data[j][0], test_data[j][1], predicted_times[j], test_data[2]])
#             print compare_data[j]
#             print '\n'
    # lowest_config = ddl_get_lowest_cost(compare_data)
    #
    # print "The lowest configuration is "
    #
    # print lowest_config








