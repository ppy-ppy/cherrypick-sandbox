import numpy as np
from config import *


def get_error(a, b):
    return (b - a) / a if b > a else 0


def calculate_measure_weight(index, table, measure):

    if measure == "io":
        measure_index = io_measure_index
    elif measure == "cpu":
        measure_index = cpu_measure_index
    else:
        raise Exception("Only 'io' or 'cpu' measures allowed!")

    first = table.cell(index + 1, measure_index[0]).value
    medium = table.cell(index + 1, measure_index[1]).value
    last = table.cell(index + 1, measure_index[2]).value

    pre_weight = get_error(first, medium)
    post_weight = get_error(medium, last)

    weight = (pre_weight + post_weight) / 2
    return weight


def get_weight(meta_jobs_length, data):
    table = data.sheets()[0]

    io_weights = []
    cpu_weights = []

    for index in range(meta_jobs_length):
        curr_io_weight = calculate_measure_weight(index, table, "io")
        curr_cpu_weight = calculate_measure_weight(index, table, "cpu")
        io_weights.append(curr_io_weight)
        cpu_weights.append(curr_cpu_weight)

    return io_weights, cpu_weights


def normalize_probabilities(p1, p2):
    normalized_p1 = p1 / (p1 + p2)
    normalized_p2 = p2 / (p1 + p2)
    return normalized_p1, normalized_p2


def get_distance((x1, y1), (x2, y2)):
    return np.sqrt(np.square(x1 - x2) + np.square(y1 - y2))


def create_samples(meta_jobs, data, sample_num):

    meta_jobs_length = len(meta_jobs)
    # input_samples = np.random.randint(0, 10, size=(int(sample_num), meta_jobs_length))

    input_01 = np.random.randint(0, 10, size=(int(sample_num), 2))
    input_24 = np.random.randint(0, 2, size=(int(sample_num), 3))
    input_samples = np.concatenate([input_01, input_24], axis=1)

    weights = np.zeros((sample_num, 2))

    io_weights, cpu_weights = get_weight(meta_jobs_length, data)

    for index in range(meta_jobs_length):
        weights[:, 0] += input_samples[:, index] * io_weights[index]
        weights[:, 1] += input_samples[:, index] * cpu_weights[index]

    weights[:, 0], weights[:, 1] = normalize_probabilities(weights[:, 0], weights[:, 1])
    weights[np.isnan(weights)] = 0.5

    label_chooser = np.zeros((sample_num, len(labels)))

    for index in range(len(labels)):
        label_chooser[:, index] = get_distance((weights[:, 0], weights[:, 1]), (labels[index][0], labels[index][1]))

    output_samples = label_chooser.argmin(axis=1)

    return input_samples, output_samples

