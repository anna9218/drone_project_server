import os
import sys
import tensorflow as tf
sys.path.append(os.getcwd().split('\SlurmFunctions\models')[0])
from SlurmFunctions.models.Model import Model

"""
    A class that inherits from a Model class
    Responsibilities of this class:
        1. Sets the first layer of the CNN model to be tf.keras.layers.GRU
"""


class modelGRU(Model):

    def __init__(self, parameters: dict = None):
        super().__init__(parameters)
        self.first_layer = tf.keras.layers.GRU(self.params['neurons_in_layer'], input_shape=(None, self.input_dim))
        self.model_type = "modelGRU"
