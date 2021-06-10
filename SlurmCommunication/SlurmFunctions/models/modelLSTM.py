import tensorflow as tf
# import Model
from SlurmCommunication.SlurmFunctions.models.Model import Model

"""
    A class that inherits from a Model class
    Responsibilities of this class:
        1. Sets the first layer of the CNN model to be tf.keras.layers.LSTM
"""


class modelLSTM(Model):

    def __init__(self, parameters: dict = None):
        super().__init__(parameters)
        self.first_layer = tf.keras.layers.LSTM(self.params['neurons_in_layer'], input_shape=(None, self.input_dim))
        self.model_type = "modelLSTM"



