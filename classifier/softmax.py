# -*- coding: utf-8 -*-
import numpy as np
from config import *


class SoftMax:
    def __init__(self, hidden_size=100, class_num=len(labels), features_num=len(meta_jobs),
                 learning_rate=1e-2, reg=1e-3):
        self.w_input_hidden = 0.01 * np.random.rand(features_num, hidden_size)
        self.b_input_hidden = np.zeros((1, hidden_size))
        self.w_hidden_output = 0.01 * np.random.rand(hidden_size, class_num)
        self.b_hidden_output = np.zeros((1, class_num))
        self.learning_rate = learning_rate
        self.reg = reg

    def train(self, input_data, label_data):

        num_data = input_data.shape[0]
        for i in range(10000):
            # ReLU activation function
            hidden_output = np.maximum(0, np.dot(input_data, self.w_input_hidden) + self.b_input_hidden)
            result = np.dot(hidden_output, self.w_hidden_output) + self.b_hidden_output  # data_num*class_num

            result = np.exp(result)
            result = result / np.sum(result, axis=1, keepdims=True)  # data_num*class_num

            coret_logresult = -np.log(result[range(num_data), label_data])
            data_loss = np.sum(coret_logresult) / input_data.shape[0]
            reg_loss = 0.5 * self.reg * np.sum(self.w_input_hidden * self.w_input_hidden) + 0.5 * self.reg * np.sum(
                self.w_hidden_output * self.w_hidden_output)  # 正则项
            loss = data_loss + reg_loss
            if i % 100 == 0:
                print("epoches: %d: loss %f" % (i, loss))

            # compute the gradient on scores
            dscores = result  # data_num*class_num
            dscores[range(num_data), label_data] -= 1  # 计算y^-y   data_num*1
            dscores /= num_data  # *(1/data_num)          输出层误差项

            # backpropate the gradient to the parameters
            # first backprop into parameters W2 and b2
            dW2 = np.dot(hidden_output.T, dscores)  # hidden_output: data_size*hidden_size
            # dW2:hidden_size*1
            db2 = np.sum(dscores, axis=0, keepdims=True)
            # next backprop into hidden layer
            dhidden = np.dot(dscores, self.w_hidden_output.T)
            # backprop the ReLU non-linearity
            dhidden[hidden_output <= 0] = 0  # 第一层的误差项
            # finally into W,b
            dW = np.dot(input_data.T, dhidden)
            db = np.sum(dhidden, axis=0, keepdims=True)

            # add regularization gradient contribution
            dW2 += self.reg * self.w_hidden_output
            dW += self.reg * self.w_input_hidden

            # perform a parameter update
            self.w_input_hidden += -self.learning_rate * dW
            self.b_input_hidden += -self.learning_rate * db
            self.w_hidden_output += -self.learning_rate * dW2
            self.b_hidden_output += -self.learning_rate * db2

    def test(self, input_data):
        # ReLU activation function
        hidden_output = np.maximum(0, np.dot(input_data, self.w_input_hidden) + self.b_input_hidden)
        result = np.dot(hidden_output, self.w_hidden_output) + self.b_hidden_output  # data_num*class_num

        result = np.exp(result)
        result = result / np.sum(result, axis=1, keepdims=True)  # data_num*class_num
        return result.argmax(axis=1)
