# from spearmint.schema import VirtualMachineType as VM
import csv
import itertools
import sys

class Grouping(object):
    def __init__(self, data_file=None):
        '''
            Initiliaze the Predictor with some training data
            The training data should be a list of [mcs, input_fraction, time]
        '''
        self.grouping_data = []
        # self.vm_name = []
        self.another_grouping_data = []
        if data_file:
            with open(data_file, 'rb') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ')
                # for i in range(len(vm_type_list)):
                for row in reader:
                    parts = row[0].split(',')
                    mc = int(parts[0])
                    scale = float(parts[1])
                    time = float(parts[2])
                    vm_type = str(parts[3])
                    if time != -2:
                        self.grouping_data.append([mc, scale, time, vm_type])
                    else:
                        self.grouping_data.append([mc, scale, 9999999999999, vm_type])

        self.scale_list = []

        self.grouping_data_dict = {}

        for i in range(len(self.grouping_data)):
            self.scale_list.append(self.grouping_data[i][1])

        self.surplus_scale_list = list(set(self.scale_list))
        self.surplus_scale_list.sort(key=self.scale_list.index)

        for row in self.grouping_data:
            if row[1] not in self.grouping_data_dict.keys():
                self.grouping_data_dict[row[1]] = [row]
            else:
                self.grouping_data_dict[row[1]].append(row)
        sorted(self.grouping_data_dict.keys())

        for value in self.grouping_data_dict.values():
            self.another_grouping_data.append(value)


    def time_based_grouping(self):

        cost_list = []

        lowest_cost_index = []

        lowest_cost_cluster_type = []

        for i in range(len(self.surplus_scale_list)):
            cost_list.append([self.surplus_scale_list[i]])

        for i in range(len(self.another_grouping_data)):
            for j in range(len(self.another_grouping_data[i])):
                # price = VM.selectBy(name=self.another_grouping_data[i][j][3]).getOne().cost
                # cost = np.log(self.another_grouping_data[i][j][0]*price)*self.another_grouping_data[i][j][2]
                cost = self.another_grouping_data[i][j][2]
                self.another_grouping_data[i][j].append(cost)

        cluster_type = []
        for i in range(len(self.another_grouping_data)):
            cluster_type.append([i])
            for j in range(len(self.another_grouping_data[i])):
                cluster_type[i].append([self.another_grouping_data[i][j][3], self.another_grouping_data[i][j][0]])

        for i in range(len(cluster_type)):
            del cluster_type[i][0]

        for i in range(len(self.another_grouping_data)):
            for j in range(len(self.another_grouping_data[i])):
                cost_list[i].append(self.another_grouping_data[i][j][4])

        for i in range(len(cost_list)):
            del cost_list[i][0]

        for i in range(len(cost_list)):
            lowest_cost_index.append(cost_list[i].index(min(cost_list[i])))

        num_times = [(k, len(list(v))) for k, v in itertools.groupby(lowest_cost_index)]

        for i in range(len(num_times)):
            num_times[i] = list(num_times[i])

        for i in range(len(num_times)):

            if num_times[i][1] < 10:
                if i < (len(num_times) - 1):
                    num_times[i + 1][1] = num_times[i][1] + num_times[i + 1][1]

        for i in range(len(num_times) - 1, -1, -1):

            if num_times[i][1] < 10:
                if i < (len(num_times) - 1):
                    del num_times[i]

        scale_group = []

        for i in range(len(num_times)):
            if i != 0:
                top = bottom + 1
                bottom = top + num_times[i][1] - 1
            elif i == 0:
                top = 0
                bottom = top + num_times[i][1] - 1
            scale_group.append(
                (self.surplus_scale_list[top], self.surplus_scale_list[bottom], cluster_type[top][num_times[i][0]]))

        scale_split = []

        fixed_data = [0.0, 1.0, 100.0]

        for i in range(len(scale_group)):
            if i == 0:
                scale_split.append(scale_group[i][0])
                scale_split.append(scale_group[i][1])
            else:
                scale_split.append(scale_group[i][1])

        scale_split.extend(fixed_data)

        scale_split = sorted(list(set(scale_split)))

        for i in range(len(scale_split)):
            scale_split[i] = int(scale_split[i])

        # print scale_split
        return scale_split