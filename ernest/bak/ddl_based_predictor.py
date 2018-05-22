import csv
import math
import sys

import numpy as np
from scipy.optimize import nnls

from ernest.bak.predictor import Predictor
from spearmint.schema import *
from spearmint.schema import VirtualMachineType as VM

# TODO: 1. experiment_data.csv, which file generates/uses it?
# TODO: 2. add an interface in main.py [Phase 5], taking in "deadline" instead of a static one
# TODO: 3. clear the folder "ernest", delete useless files
#
#
# class Descide(object):
#
#
#     def __init__(self):
#         return self
#
#
#     def DeadlineDescide(self, predictor_time, deadline):

FILE_PATH = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(FILE_PATH, "lowest.csv")
INPUT_PATH = os.path.join(FILE_PATH, "rcv1-parsed.csv")
deadline = 60


def establish_csv():
    csv_file = open(OUTPUT_PATH, 'w')
    writer = csv.writer(csv_file)
    writer.writerow(['Machines', 'Time', 'Cost'])
    return None


def get_predictor_time():



    predicted_data=[]

    pred = Predictor(data_file=INPUT_PATH)

    model = pred.fit()

    test_data = [[i, 1.0] for i in xrange(4, 128, 4)]

    predicted_times = pred.predict_all(test_data)

    for i in xrange(0, len(test_data)):
        predicted_data.append([test_data[i][0]])
        predicted_data[i].append(predicted_times[i])

    for i in range(len(predicted_data)):
        for j in range(len(predicted_data[i])):
            predicted_data[i][j] = float(predicted_data[i][j])
    return predicted_data


def in_time_predicted(compare_data):
    in_time_data = []

    for i in range(len(compare_data)):
        if compare_data[i][2] <= deadline:
            in_time_data.append(compare_data[i])
            # del predictor_data[i]
        else:
            continue
    return in_time_data


def get_lowest_cost(compare_data):
    in_time_data = in_time_predicted(compare_data)
    cost = []
    lowest_cost_configuration = []
    print "###################"
    for i in range(len(in_time_data)):
        price = VM.selectBy(name = in_time_data[i][1]).getOne().cost
        cost.append(math.log(price)*in_time_data[i][0]*in_time_data[i][2])
        # cost.append(in_time_data[i][0]*in_time_data[i][1]*price)

    lowest_cost = min(cost)
    a = cost.index(lowest_cost)
    lowest_cost_configuration.append(in_time_data[a][0])
    lowest_cost_configuration.append(in_time_data[a][1])
    lowest_cost_configuration.append(lowest_cost)

    # if not os.path.exists(OUTPUT_PATH):
    #     self.establish_csv()
    #     with open(OUTPUT_PATH, 'a') as csv_file:
    #         writer = csv.writer(csv_file)
    #         writer.writerow(lowest_cost_configuration)
    #
    # else:
    #     with open(OUTPUT_PATH, 'a') as csv_file:
    #         writer = csv.writer(csv_file)
    #         writer.writerow(lowest_cost_configuration)
    return lowest_cost_configuration

class Predictor(object):
    def __init__(self, training_data_in=[], data_file=None):
        '''
            Initiliaze the Predictor with some training data
            The training data should be a list of [mcs, input_fraction, time]
        '''
        self.training_data = []
        self.training_data.extend(training_data_in)
        if data_file:
            with open(data_file, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ')
                for row in reader:
                    if row[0][0] != '#':
                        parts = row[0].split(',')
                        vm_type = str(parts[1])
                        cpus = int(parts[2])
                        ram = float(parts[3])
                        mc = int(parts[4])
                        scale = float(parts[7])
                        time = float(parts[5])
                        self.training_data.append([mc, cpus, ram, scale, time, vm_type])

    # def add(self, mcs, input_fraction, time):
    #     self.training_data.append([mcs, input_fraction, time])

    def predict(self, input_fraction, cpus, ram, mcs):
        '''
            Predict running time for given input fraction, number of machines.
        '''
        # print "predict"
        test_features = np.array(self._get_features([input_fraction, cpus, ram, mcs]))
        return test_features.dot(self.model[0])

    def predict_all(self, test_data):
        '''
            Predict running time for a batch of input sizes, machines.
            Input test_data should be a list where every element is (input_fraction, machines)
        '''
        # print "all"
        test_features = np.array([self._get_features([row[0], row[1], row[2], row[3]]) for row in test_data])
        return test_features.dot(self.model[0])

    def fit(self):
        print "Fitting a model with ", len(self.training_data), " points"
        labels = np.array([row[4] for row in self.training_data])
        # print "fit"
        data_points = np.array([self._get_features(row) for row in self.training_data])
        self.model = nnls(data_points, labels)
        # TODO: Add a debug logging mode ?
        # print "Residual norm ", self.model[1]
        # print "Model ", self.model[0]
        # Calculate training error
        training_errors = []
        for p in self.training_data:
            print "###"
            print p[4]
            predicted = self.predict(p[3], p[1], p[2], p[0])
            training_errors.append(predicted / p[4])

            # print "#######"
            print predicted
        print "Average training error %f%%" % ((np.mean(training_errors) - 1.0) * 100.0)
        return self.model[0]

    def num_examples(self):
        return len(self.training_data)

    def _get_features(self, training_point):
        # print "*****************"
        # print training_point
        mc = training_point[0]
        scale = training_point[3]
        CPU = training_point[1]
        RAM = training_point[2]
        # print np.log(CPU)
        # print np.log(RAM)
        return [1, float(scale) / (float(mc)*np.log(CPU)*np.log(RAM)), np.log(mc), float(mc)]

    # def get_test_data(self):
    #     test_data_list = []
    #     csv_reader = csv.reader(open('rcv1-parsed.csv'))
    #     for row in csv_reader:
    #         test_data_list.append(row)
    #     print test_data_list

    def train_data(self):
        # print self.training_data
        return self.training_data


        # def get_predicted_data(self):


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage <predictor.py> <csv_file_train>"
        sys.exit(0)

    predictor_data = []

    pred = Predictor(data_file=sys.argv[1])

    model = pred.fit()

    print model

    train_data = pred.train_data()

    test_data = []
    compare_data = []

    print "change mc number"
    print train_data
    for i in range(len(train_data)):
        # for j in range(1, 6):
        #     j += 0.5
        test_data.append([train_data[i][0], train_data[i][1], train_data[i][2], 3, train_data[i][5]])
    predicted_times = np.ndarray.tolist(pred.predict_all(test_data))
    for j in range(len(train_data)):
        compare_data.append([train_data[j][0],train_data[j][5],predicted_times[j]])
        print compare_data[j]
    lowest_config = get_lowest_cost(compare_data)
    print lowest_config

    for i in xrange(0, len(test_data)):
        predictor_data.append([test_data[i][0]])
        predictor_data[i].append(predicted_times[i])
