import numpy as np
from scipy.optimize import nnls
import csv


class NnlsPredictor(object):
    def __init__(self, name, training_data_in=[], data_file=None):
        """
            Initiliaze the Predictor with some training data
            The training data should be a list of [mcs, input_fraction, time]
        """
        self.training_data = []
        self.name = name

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

    def _get_features(self, training_point):
        mc = training_point[0]
        scale = training_point[1]

        return [1.0, float(scale) / float(mc), float(mc), np.log(mc)]

    def predict(self, mcs, input_fraction):
        """
            Predict running time for given input fraction, number of machines.
        """
        test_features = np.array(self._get_features([mcs, input_fraction]))
        return test_features.dot(self.model[0])

    def predict_all(self, test_data):
        """
            Predict running time for a batch of input sizes, machines.
            Input test_data should be a list where every element is (input_fraction, machines)
        """
        test_features = np.array([self._get_features([row[0], row[1]]) for row in test_data])
        return test_features.dot(self.model[0])

    def fit(self, training_point):
        # print "Fitting a model with ", len(training_point), " points"
        labels = np.array([row[2] for row in training_point])
        data_points = np.array([self._get_features(row) for row in training_point])
        self.model = nnls(data_points, labels)
        # TODO: Add a debug logging mode ?
        training_errors = []
        for p in training_point:
            predicted = self.predict(p[0], p[1])
            training_errors.append(predicted / p[2])

        # print "Average training error %f%%" % ((np.mean(training_errors) - 1.0) * 100.0)
        return self.model[0]

    def train_data(self):
        return self.training_data









