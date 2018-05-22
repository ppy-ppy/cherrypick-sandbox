import numpy as np
import scipy
from scipy.optimize import nnls
import csv
import sys
from spearmint.schema import VirtualMachineType as VM


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
                        vm_type = str(parts[3])
                        mc = int(parts[0])
                        scale = float(parts[1])
                        time = float(parts[2])
                        self.training_data.append([mc, scale, time, vm_type])

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
            # print p
            print predicted
            # if (p[3]==self.training_data[3])&(p[1]==self.training_data[1])&(p[2]==self.training_data[2])&(p[0]==self.training_data[0]):
            #     print p[4]
            training_errors.append(predicted / p[4])

            # print "#######"
            # print predicted
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
        return [1.0, float(scale) / (float(mc)*float(CPU)), np.log(mc), float(mc)]

    # def get_test_data(self):
    #     test_data_list = []
    #     csv_reader = csv.reader(open('rcv1-parsed.csv'))
    #     for row in csv_reader:
    #         test_data_list.append(row)
    #     print test_data_list

    def train_data(self):
        # print "!!!!!!!!!!!!!"
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

    # print train_data

    test_data = []

    predicted_times_list = []

    print "change mc number"
    for i in range(len(train_data)):
        for j in range(1, 10, 1):
            test_data.append([train_data[i][0], train_data[i][1], train_data[i][2], j, train_data[i][4]])
    predicted_times = pred.predict_all(test_data)
    print len(test_data)
    print len(list(predicted_times))

    temp_list = test_data

    for i in range(0, len(test_data)-1):
        temp_list[i].append(predicted_times[i])
    predicted_times_list = temp_list
    # print predicted_times_list

    for i in xrange(0, len(test_data)):
        predictor_data.append([test_data[i][0]])
        predictor_data[i].append(predicted_times[i])



        # print "change scale"
        # for i in range (17):
        #     # print i
        #     if (i == 2)|(i == 4)|(i == 8)|(i == 16):
        #         test_data = [[i, train_data[j][1], train_data[j][2], train_data[j][3], 1.0]]
        #         predicted_times = pred.predict_all(test_data)
        #         print test_data
                # print train_data[j]
                # print predicted_times

    # for j in range(len(train_data)):
    #     test_data = [[train_data[j][0], , train_data[j][2], train_data[j][3], 1.0] for i in range(1, 4)]
    #     predicted_times = pred.predict_all(test_data)
    #     print "change scale"
    #     print predicted_times



    # predicted_times = pred.predict_all(test_data)
    # print
    # print "Machines, Predicted Time"
    # for i in xrange(0, len(test_data)):
    #     # print test_data[i][0], predicted_times[i]
    #     predictor_data.append([test_data[i][0]])
    #     predictor_data[i].append(predicted_times[i])
        # print predictor_data

