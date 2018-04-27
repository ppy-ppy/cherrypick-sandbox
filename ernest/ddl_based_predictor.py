from predictor import Predictor
import csv
import math
import os
from spearmint.schema import *
from sqlobject import *
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
deadline = 100000
price = 5

FILE_PATH = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(FILE_PATH, "lowest.csv")
INPUT_PATH = os.path.join(FILE_PATH, "rcv1-parsed.csv")


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
    # print
    # print "Machines, Predicted Time"
    # print model
    for i in xrange(0, len(test_data)):
        # print test_data[i][0], predicted_times[i]
        predicted_data.append([test_data[i][0]])
        predicted_data[i].append(predicted_times[i])
    # print predictor_data
    for i in range(len(predicted_data)):
        for j in range(len(predicted_data[i])):
            predicted_data[i][j] = float(predicted_data[i][j])
    return predicted_data


def in_time_predicted():
    predicted_data = get_predictor_time()
    in_time_data = []

    for i in range(len(predicted_data)):
        # print i
        if predicted_data[i][1] <= deadline:
            in_time_data.append(predicted_data[i])
            # del predictor_data[i]
        else:
            continue
    return in_time_data


def get_lowest_cost():
    in_time_data = in_time_predicted()
    cost = []
    lowest_cost_configuration = []
    for i in range(len(in_time_data)):
        cost.append(math.log(price)*in_time_data[i][1])
        # cost.append(in_time_data[i][0]*in_time_data[i][1]*price)

    lowest_cost = min(cost)
    a = cost.index(lowest_cost)
    lowest_cost_configuration.append(in_time_data[a][0])
    lowest_cost_configuration.append(in_time_data[a][1])
    lowest_cost_configuration.append(lowest_cost)

    if not os.path.exists(OUTPUT_PATH):
        establish_csv()
        with open(OUTPUT_PATH, 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(lowest_cost_configuration)

    else:
        with open(OUTPUT_PATH, 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(lowest_cost_configuration)
    # with open('test.csv', 'w', newline='') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerow(["Machines", "TIME", "COST"])
    #     writer.writerow(lowest_cost_configuration)

    return lowest_cost_configuration


if __name__ == '__main__':
    best_config = get_lowest_cost()
    print "according to deadline the lowest cost configuration"
    print "machines  TIME   COST"
    print best_config
