from spearmint.schema import *
import csv
import os
import math


def establish_csv():
    csvfile = open('test.csv', 'w')
    writer = csv.writer(csvfile)
    writer.writerow(['# Experiment', 'VirtualMachine', 'MachinesNumber', 'Time', 'Cost'])
    return None


def output_test_time_ernest(vm, cluster_size, exp_name, time):
    exp = Experiment.find(exp_name)
    runs = exp.find_runs(vm, int(cluster_size))
    vm_type = runs[0].config
    # cost = VirtualMachineType.selectBy(id=vm_type.vmID).getOne().cost
    total_cost = math.log(runs[0].cost)*time
    total_cost = str(total_cost)
    outputdata = []
    outputdata.append(exp_name)
    outputdata.append(vm)
    outputdata.append(cluster_size)
    outputdata.append(time)
    outputdata.append(total_cost)

    if not os.path.exists("test.csv"):
        establish_csv()
        with open('test.csv', 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(outputdata)

    else:
        with open('test.csv', 'a') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(outputdata)

    print vm_type.count
    # print cost
    print time
    print total_cost
    print outputdata


# output_test_time_ernest("c3.xlarge", 2, "terasort", 50)