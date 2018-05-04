from __future__ import division
from softmax import SoftMax
from train_classifier import create_samples
from config import *
import numpy as np


def get_distribution(output):
    distribution = [0] * len(labels)
    for i in output:
        distribution[i] += 1

    return distribution


def train_classifier(softmax, training_num):
    training, output = create_samples(meta_jobs, data, training_num)
    distribution = get_distribution(output)

    softmax.train(training, output)
    parameters = "w_input_hidden = " + str(softmax.w_input_hidden.tolist()) + \
                 "\nb_input_hidden = " + str(softmax.b_input_hidden.tolist()) + \
                 "\nw_hidden_output = " + str(softmax.w_hidden_output.tolist()) + \
                 "\nb_hidden_output = " + str(softmax.b_hidden_output.tolist())
    file_object = open(parameter_output, 'w')
    file_object.write(parameters)
    file_object.close()
    return distribution


def get_accuracy(softmax, testing_num):
    testing, output = create_samples(meta_jobs, data, testing_num)
    distribution = get_distribution(output)

    output_test = softmax.test(testing)
    errors = np.sum(output != output_test)
    error_rate = errors / testing_num

    distribution_test = get_distribution(output_test)

    return 1 - error_rate, distribution, distribution_test


if __name__ == '__main__':
    softmax = SoftMax()
    print train_classifier(softmax, 400)
    print get_accuracy(softmax, 100)

