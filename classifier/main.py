from __future__ import division
from softmax import SoftMax
from train_classifier import create_samples, get_weight, normalize_probabilities
from config import *
import numpy as np
from parameters import *


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


def softmax_classifier(input_data):

    io_weights, cpu_weights = get_weight(len(meta_jobs), data)

    io_weight = 0
    cpu_weight = 0

    for index in range(len(meta_jobs)):
        io_weight += input_data[index] * io_weights[index]
        cpu_weight += input_data[index] * cpu_weights[index]

    if io_weight == 0 and cpu_weight == 0:
        io_weight = 0.5
        cpu_weight = 0.5
    else:
        io_weight, cpu_weight = normalize_probabilities(io_weight, cpu_weight)

    hidden_output = np.maximum(0, np.dot(input_data, w_input_hidden) + b_input_hidden)
    result = np.dot(hidden_output, w_hidden_output) + b_hidden_output  # data_num*class_num
    result = np.exp(result)
    result = result / np.sum(result, axis=1, keepdims=True)  # data_num*class_num

    return (io_weight, cpu_weight), result.argmax(axis=1)[0]


if __name__ == '__main__':
    # softmax = SoftMax()
    # print train_classifier(softmax, 400)
    # print get_accuracy(softmax, 100)
    print softmax_classifier([0, 10, 0, 0, 0])
    print softmax_classifier([1, 3, 1, 1, 0])
