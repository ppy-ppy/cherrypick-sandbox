from classifier.train_classifier import get_weight, normalize_probabilities
from classifier.config import *
import numpy as np
from classifier.parameters import *


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

