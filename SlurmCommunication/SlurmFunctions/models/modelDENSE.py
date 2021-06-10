import tensorflow as tf
from SlurmCommunication.SlurmFunctions.models.Model import Model
# import Model

"""
    A class that inherits from a Model class
    Responsibilities of this class:
        1. Sets the first layer of the CNN model to be tf.keras.layers.Dense
"""


class modelDENSE(Model):

    def __init__(self, parameters: dict = None):
        super().__init__(parameters)
        self.first_layer = tf.keras.layers.Dense(self.params['neurons_in_layer'], input_shape=(None, self.input_dim))
        self.model_type = "modelDENSE"

    # def set_first_layer(self):
    #     self.first_layer = tf.keras.layers.Dense(self.params['neurons_in_layer'], input_shape=(None, self.input_dim))
