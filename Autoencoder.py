"""
Justin Keeling
Alex Harry
John Lambrecht
Andrew Smith

Institution: Montana State University
Course: CSCI-447 Machine Learning
Instructor: John Shepherd

File: contains classes and functions that are used primarily for the purpose of creating an AutoEncoder
"""

import random
import math
import numpy as np


class AutoEncoder:
    """
    An AutoEncoder is an unsupervised algorithm and is also a neural network. The difference between the neural network
    and the auto encoder is that the target function is the input.

    Three layers: Input, hidden, and output
    Structure: Encoder and Decoder
    Encoder: Compresses data. or maps input data into a hidden representation.
    Decoder: Reconstructs the data back to the input.

    Specifics: uses back propagation to tune and train. Utilizes Feed forward.

    This class contains functions to structure, fit, and  predict auto encoders.
    """

    def __init__(self, num_layers, is_stacked, num_hidden_layers, io_size, eta, alpha):
        """
        Initializes an AutoEncoder object.
        :param num_layers: int ; arbitrarily set the number of hidden layers
        :param is_stacked: boolean ; to determine if the encoder is feeding another encoder
        :param num_hidden_layers: list ; number of  hidden layer nodes
        :param io_size: int ; input and output layer node size
        """
        self.is_stacked = is_stacked  # controls whether two or more encoders involved
        self.input_size = io_size
        self.output_size = io_size
        self.hidden_node_sizes = num_hidden_layers  # vector of hidden layer node size
        self.num_hidden_layers = num_layers
        self.input_layer = None
        self.current_layer = None
        self.output_layer = None
        self.eta = eta
        self.alpha = alpha

    def initialize_auto_encoder(self, data_obj):
        """
        Create the structure of the neural network
        :return: None
        """
        df = data_obj.train_df
        first_iter = True  # create structure first iteration
        batch_size = 10  # number of example per batch  # TODO: use stochastic gradient descent... idk where batch size matters.
        j = 0
        batch = []
        for row in df.iterrows():  # iterate through each example
            if first_iter:  # first iteration sets up structure
                self.input_layer = Layer(self.input_size, True, False, row, None)  # create hidden layer
                self.current_layer = self.input_layer
                self.create_hidden_layer(self.num_hidden_layers,
                                         self.hidden_node_sizes)  # create layers in hidden layer
                self.output_layer = Layer(self.output_size, False, True, None, self.current_layer)
                self.current_layer.set_next_layer(self.output_layer)  # connect last hidden to output
                first_iter = False  # does not let a new structure to overwrite existing
            """
            training_process: feed forward, cost_process, back propagation (includes updating by using gradient descent)
            """
            j += 1
            if j % batch_size == 0:
                self.gradient_descent(batch)
                batch = []
            batch.append(row)
            # self.feed_forward_process()  # creates sigmoid values for every node
            # self.predict()  # TODO: finish function
            # self.cost_process()  # TODO: finish function
            # self.back_propagation_process()  # updates the weights, bias, and node values using gradient descent. # TODO finish function

    def initialize_stacked_auto_encoder(self, data_obj):  # , #num_layers, num_hidden_layer):
        """
        Initializes another auto encoder such that the current auto encoder is
        :param data_obj:
        :return:
        """
        df = data_obj.train_df
        first_iter = True  # create structure first iteration
        batch_size = 10  # number of example per batch  # TODO: use stochastic gradient descent... idk where batch size matters.
        for row in df.iterrows():  # iterate through each example
            if first_iter:  # first iteration sets up structure
                self.input_layer = Layer(self.input_size, True, False, row, None)  # create hidden layer
                self.current_layer = self.input_layer
                inner_encoder = AutoEncoder(self.num_hidden_layers, True, [3],
                                            self.hidden_node_sizes[0])  # int, bool, list, int
                inner_encoder.input_layer = Layer(inner_encoder.input_size, True, False, None, self.input_layer)
                inner_encoder.current_layer = inner_encoder.input_layer
                self.current_layer.set_next_layer(inner_encoder.current_layer)
                inner_encoder.create_hidden_layer(inner_encoder.num_hidden_layers, inner_encoder.hidden_node_sizes)
                inner_encoder.output_layer = Layer(inner_encoder.output_size, False, True, None,
                                                   inner_encoder.current_layer)
                inner_encoder.current_layer.set_next_layer(inner_encoder.output_layer)
                self.current_layer = inner_encoder.output_layer
                self.output_layer = Layer(self.output_size, False, True, None, self.current_layer)
                self.current_layer.set_next_layer(self.output_layer)  # connect last hidden to output
                first_iter = False

    def create_hidden_layer(self, num_layers, num_nodes):
        """
        Create the hidden layer's layers
        :param num_layers: number of hidden layers
        :param num_nodes: list; number of nodes in hidden layer
        :return: None
        """
        # TODO: number of nodes will decrease by 1 until size 1, then expand back out...
        print(num_layers)
        print(num_nodes)
        if len(num_nodes) is 1:
            new_layer = Layer(num_nodes[0], False, False, None, self.current_layer)
            self.current_layer.set_next_layer(new_layer)
            temp = self.current_layer
            self.current_layer = temp.get_next_layer()
        else:
            for i in range(num_layers):  # create the user-defined number of layers
                new_layer = Layer(num_nodes[i], False, False, None, self.current_layer)
                self.current_layer.set_next_layer(new_layer)  # link from current to next layer
                temp = self.current_layer
                self.current_layer = temp.get_next_layer()

    @staticmethod
    def sigmoid_activation_process(current):
        """
        Given the current layer (can be input), get the next layer. For each node in next layer, calculate the Wa+b
        :param current:
        :return: None
        """
        # TODO: linear activation at output
        current_layer = current
        next_layer = current_layer.get_next_layer()  # next layer to calculate Z and sigmoid for.
        for target_node in next_layer.nodes:  # for each node in the next layer, calculate activation function
            sum_value = 0
            for node, weight in zip(current_layer.nodes,
                                    target_node.weight_vector):  # iterate through current layer nodes in parallel to the weights of the target node (target node has previous layer size weights).
                sum_value += node.get_value() * weight  # multiply weights and value
            sum_value += target_node.bias  # add in bias last
            target_node.z_value = sum_value  # value to sigmoid
            target_node.sigmoid_function()  # creates the a range between [0, 1] from the value z.
        current = current_layer

    def predict(self):
        # TODO: compare the output layer's values to the input layers (since actual is the input values).
        # TODO: Traditional Neural net: actual values are all 0 but one is 1. Since we are trying to predict the input layer, we cannot do that.
        pass

    def cost_process(self):
        """
        Calculate the difference from the predicted - actual and use means squared.
        :return: None
        """
        # TODO: goal; we want (predicted - actual)^2 = 0
        coefficient = 1 / self.output_size
        sum_value = 0
        for node in self.output_layer.nodes:
            pass

    def back_propagation_process(self):
        while self.current_layer.get_previous_layer() != None:
            if self.current_layer.is_output_layer:
                j = 0
                for node in self.current_layer.nodes:
                    node.delta = -(self.input_layer.nodes.value[j] - node.get_value())
                    node.bias_change += node.delta
                    j += 1
                    i = 0
                    for weight in node.weight_vector:
                        node.weight_change_vector[i] = node.delta * weight
            else:
                f = 0
                for node in self.current_layer.nodes:
                    summer = 0
                    for noder in self.current_layer.get_next_layer().nodes:
                        summer += noder.delta * noder.weight[f]
                    node.delta = node.get_value * (1 - node.value) * summer
                    node.bias_change += node.delta
                    u = 0
                    for weight in node.weight_vector:
                        node.weight_change_vector[u] += node.delta * self.current_layer.get_previous_layer().nodes[
                            u].value
                    f += 1
            self.current_layer = self.current_layer.get_previous_layer()
        return

    def gradient_descent(self, batch):
        # TODO: not sure if needed for back prop... not mentioned in assignment
        for input in batch:
            j = 0
            for node in self.input_layer.nodes:
                node.value = input[j]
                j += 1
            self.feed_forward_process()
            self.back_propagation_process()
        self.current_layer = self.output_layer
        while self.current_layer.get_previous_layer() != None:
            for node in self.current_layer.nodes:
                node.previous_bias_change = -self.eta * node.bias_change / len(
                    batch) + self.alpha * node.previous_bias_change
                node.bias += node.previous_bias_change
                node.bias_change = 0
                i = 0
                for weight in node.weight_vector:
                    node.previous_weight_change[i] = -self.eta * node.weight_change_vector[i] / len(
                        batch) + self.alpha * node.previous_weight_change[i]
                    weight += node.previous_weight_change[i]
                    node.weight_change_vector[i] = 0
                    i += 1
            self.current_layer = self.current_layer.get_previous_layer()
        return

    def feed_forward_process(self):
        """
        Goes through network nodes and finds the sigmoid value for each node.
        :return: None
        """
        self.current_layer = self.input_layer
        while self.current_layer is not self.output_layer:  # once it is the output layer, no sigmoid value to compute
            self.sigmoid_activation_process(self.current_layer)  # performs sigmoid functions for layer
            self.current_layer = self.current_layer.get_next_layer()

    def print_layer_neuron_data(self):
        self.current_layer = self.input_layer
        while True:
            self.current_layer.print_layer_data()
            for node in self.current_layer.nodes:
                node.print_neuron_data()
                pass
            if self.current_layer is self.output_layer:
                break
            else:
                self.current_layer = self.current_layer.get_next_layer()


# TODO: determine if class NetworkClient is needed... See program 4


class Layer:
    """
    Creates the layers in the network of the encoder.
    Structure as a linked list essentially.
    """

    def __init__(self, num_nodes, is_input_layer, is_output_layer, input, prev=None):
        """
        Initialize a layer in the Neural Network.
        :param num_nodes: the number of nodes in the network
        :param is_input_layer: boolean var to specify if it is the input layer
        :param is_output_layer: boolean var to specify if it is the output layer
        """
        self.is_input_layer = is_input_layer
        self.is_output_layer = is_output_layer

        self.no_of_nodes = num_nodes

        self.nodes = []

        # TODO: determine if needed. Should consider iff we can do matrix multiplications...
        # self.weight_matrix = None  # a row is all the nodes in previous layer connected to a node in this layer
        # self.bias_vector = []  # contains the bias values with respect to the nodes

        self._previous_layer = prev
        self._next_layer = None

        self._initialize_layer(input)  # creates the layer

    def _initialize_hidden_nodes(self, weight_matrix, bias_vector):
        """
        initializes nodes within the layer.
        :param bias_vector: the bias for all the nodes in a list
        :param weight_matrix: a matrix of weights associated to the previous layer
        :return: nodes list of Neurons
        """
        input = [0] * self.no_of_nodes  # input is 0 for non input layer nodes; sigmoid not calculated
        nodes = []  # list to hold nodes
        for neuron in range(self.no_of_nodes):
            n = Neuron(input[neuron], bias_vector[neuron], [])
            for w in weight_matrix:
                n.weight_vector.append(w[neuron])
            nodes.append(n)
        return nodes

    def _initialize_weights(self):
        """
        Randomly initialize weights and bias vector entries.
        :return: weight matrix and vector
        """
        weight_matrix = []
        bias_vector = []
        size = self.get_previous_layer().no_of_nodes
        for i in range(size):  # iterate through number of nodes in previous layer
            weight_vector = []
            for j in range(self.no_of_nodes):  # iterate through number of nodes in current layer
                weight_vector.append(random.uniform(-1, 1))  # random value inserted into vector
            weight_matrix.append(weight_vector)  # append the vector into the matrix
        for i in range(self.no_of_nodes):
            bias_vector.append(float(random.uniform(-1, 1)) / 100)  # random initialized bias
        return weight_matrix, bias_vector

    def _initialize_layer(self, input):
        """
        initializes the layer using the other initializing functions.
        :return: None
        """
        if self.is_input_layer and input is not None:  # initialize input layer
            for i in input[1]:
                self.nodes.append(Neuron(i, None, None))
        else:  # initialize hidden_layer and output
            weight_matrix, bias_vector = self._initialize_weights()
            self.nodes = self._initialize_hidden_nodes(weight_matrix, bias_vector)

    def get_next_layer(self):
        """
        Getter function for the previous layer
        :return: next layer ; type Layer
        """
        return self._next_layer

    def get_previous_layer(self):
        """
        Getter function for previous layer
        :return: previous layer ; type Layer
        """
        return self._previous_layer

    def set_next_layer(self, next_layer):
        """
        Link to the next layer
        :param next_layer:
        :return: None
        """
        self._next_layer = next_layer

    def set_previous_layer(self, prev_layer):
        """
        Link for to the previous layer
        :param prev_layer:
        :return: None
        """
        self._previous_layer = prev_layer

    def print_layer_data(self):
        if self.is_input_layer:
            string = "_________________________________________________________________"
            center = "Input Layer"
            print(string)
            print(center)
            print(string)
            print("Next Layer Nodes = %s" % self.get_next_layer().nodes)
        if self.is_output_layer:
            string = "_________________________________________________________________"
            center = "Output Layer"
            print(string)
            print(center)
            print(string)
            print("Previous Layer Node= %s" % self.get_previous_layer().nodes)
        if self.is_output_layer == False and self.is_input_layer == False:
            string = "_________________________________________________________________"
            center = "Hidden Layer"
            print(string)
            print(center)
            print(string)
            print("Next Layer Nodes = %s" % self.get_next_layer().nodes)
            if not self.get_previous_layer().is_input_layer:
                print("Previous Layer Node= %s" % self.get_previous_layer().nodes)
            else:
                print("Previous Layer Node= Input Layer")

        print("Number of Nodes = %s" % self.no_of_nodes)
        print("Nodes = %s" % self.nodes)


class Neuron:
    """
    creates the neurons within a layer.
    """

    def __init__(self, value, bias, weight_vector):
        """
        Initialize a neuron in a layer
        :param value: the value it currently contains
        :param bias: the bias associated to the node
        :param weight_vector: the weights associated to the node with respect to the previous layers nodes
        """
        self._value = value
        self.bias = bias
        self.weight_vector = weight_vector
        self.delta = 0
        self.z_value = 0
        if weight_vector is not None:
            self.weight_change_vector = [0] * len(self.weight_vector)
        else:
            self.weight_change_vector = None
        self.bias_change = 0
        self.weight_change_vector = [0] * len(weight_vector)
        self.previous_bias_change = 0
        self.previous_weight_change = [0] * len(weight_vector)



def adjust_bias(self, amount):
    """
    PLAN to give the location of the weight to adjust and a positive or negative value to adjust by.
    :param amount: amount to adjust by
    :return: None
    """
    pass


def adjust_weight(self, location, amount):
    """
    PLAN to give the location of the weight to adjust and a positive or negative value to adjust by.
    :param location: location of the weight to change
    :param amount: amount to adjust by
    :return: None
    """
    pass


def change_value(self, new_val):
    """
    overwrite old value with new calculated value
    :param new_val:
    :return: None
    """
    self._value = new_val


def get_value(self):
    """
    getter function for value, either a sigmoidal value or a feature in the example
    :return: value ; type float
    """
    return self._value


def sigmoid_function(self):
    """
    activation function for node
    :return: None
    """
    self._value = 1 / (1 + np.exp(-self.z_value))


def print_neuron_data(self):
    print("\t----------Neuron------------")
    print("\t value = %s" % self.get_value())
    print("\t bias = %s" % self.bias)
    if self.weight_vector is not None:
        print("\t weight_vector = ", list(self.weight_vector), "\n")
    else:
        print("\t weight_vector = ", None, "\n")

# TODO: not being used, at least not yet... using vectors and matrices currently...
# class Weight:
#     """
#     creates the weights associated to a neuron within a layer
#     """
#     def __init__(self, L_neuron, R_neuron):
#         self.L_neuron = L_neuron
#         self.R_neuron = R_neuron
#         self.weight = float(random.randint(-1, 1)) / 100
#         self.weight_change = 0
#         self.prev_change = 0
#         self.momentum_cof = .5
#         self.eta = .1
#
#     def set_weight(self, weight):
#         self.weight = weight
