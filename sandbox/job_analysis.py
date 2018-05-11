from classifier.config import *
from classifier import train_classifier
import pandas as pd


def get_measure_weight(row, measure):

    if measure == "io":
        measure_index = io_measure_index
    elif measure == "cpu":
        measure_index = cpu_measure_index
    else:
        raise Exception("Only 'io' or 'cpu' measures allowed!")

    first = row[measure_index[0] - 1]
    medium = row[measure_index[1] - 1]
    last = row[measure_index[2] - 1]

    pre_weight = train_classifier.get_error(first, medium)
    post_weight = train_classifier.get_error(medium, last)

    weight = (pre_weight + post_weight) / 2
    return weight


def get_normalized_weights(row):
    io_weight = get_measure_weight(row, "io")
    cpu_weight = get_measure_weight(row, "cpu")

    normalized_io_weight, normalized_cpu_weight = train_classifier.normalize_probabilities(io_weight, cpu_weight)

    return normalized_io_weight, normalized_cpu_weight


def get_io_cpu_analysis(job_id):

    table = pd.read_excel(data, engine='xlrd', index_col='job_id')
    row = table.loc[job_id]

    normalized_io_weight, normalized_cpu_weight = get_normalized_weights(row)
    return normalized_io_weight, normalized_cpu_weight


if __name__ == '__main__':
    io_weight, cpu_weight = get_io_cpu_analysis("terasort")
    print io_weight, cpu_weight