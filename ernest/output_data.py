from spearmint.schema import *
import csv
import os
import math

FILE_PATH = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(FILE_PATH, "output.csv")


def establish_csv():
    csv_file = open(OUTPUT_PATH, 'w')
    writer = csv.writer(csv_file)
    writer.writerow(['# Experiment', 'VirtualMachine', 'MachinesNumber', 'Time', 'Cost'])
    return None


def output_test_time_ernest(vm, cluster_size, exp_name, time, scale):
    exp = Experiment.find(exp_name)
    runs = exp.find_runs(vm, int(cluster_size))
    vm_type = runs[0].config
    # cost = VirtualMachineType.selectBy(id=vm_type.vmID).getOne().cost
    total_cost = math.log(runs[0].cost)*time
    total_cost = str(total_cost)
    output_data = [exp_name, vm, cluster_size, time, total_cost]

    if not os.path.exists(OUTPUT_PATH):
        establish_csv()
        with open(OUTPUT_PATH, 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(output_data)

    else:
        with open(OUTPUT_PATH, 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(output_data)

    print vm_type.count
    # print cost
    print time
    print total_cost
    print output_data