import sys
import numpy as np
import tensorflow as tf

"""
    This is the main model class. 
    Responsibilities of this class:
        1. Holds the default CNN parameters (optimizer, metrics, iterations, batch_size, epochs, neurons_in_layer)
        2. Initialize the CNN model's parameters (listed above)
        3. Uses tensorflow library in order to CREATE, BUILD, TRAIN and PREDICT a CNN model 
        4. Each model class, should inherits from this class.
"""


class Model:
    model = None
    first_layer = None
    # the params values must be initialized with the correct types (int, str, list(str), ...) and default values
    params: dict = {'optimizer': "adam",
                    'metrics': ['accuracy'],
                    'iterations': 0,
                    'batch_size': 0,
                    'epochs': 0,
                    'neurons_in_layer': 0}
    input_dim = 360  # 360 is the number of features, size of input. 3*120 [3 is xyz, 120 is samples during the flight].
    # 3 layers in each model, last one is dense
    output_size = 4  # labels are from 0 to 9
    prediction_variable: dict = {}
    results: list = []
    X_train = []
    y_train = []
    X_test = []
    y_test = []
    model_type = "BasicModel"

    def __init__(self, parameters: dict = None):
        if parameters is not None:
            self.set_parameters_vals(parameters)

    def get_parameters(self) -> list:
        """
            1. Returns the model's parameters list
            ex: [["optimizer", str, optimizer_default_value],
                 ["metrics", list(str), metrics_default_value], ...]
        """
        params_and_types = []
        for key in self.params.keys():
            params_and_types.append([key, type(self.params[key]).__name__, self.params[key]])
        return params_and_types

    def set_parameters_vals(self, params_val: dict) -> bool:
        """
            2. Set values to the model's parameters
        :param params_val: {param1: val1, param2: val2}
        """
        for key in params_val.keys():
            self.params[key] = params_val[key]

    def set_output_size(self, output_size):
        self.output_size = output_size

    def build_model(self):
        self.model = tf.keras.models.Sequential([
            self.first_layer,
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dense(self.output_size)]
        )
        self.model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                           optimizer=self.params['optimizer'],
                           metrics=self.params['metrics'])

    def set_train_test_sets(self, X_train, y_train, X_test, y_test):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def train_and_predict_model(self):
        """
            7. Train the model on the selected train_dataset and test_dataset
        :return:
        """
        eval_sum = 0
        for i in range(self.params['iterations']):
            self.build_model()
            # train model
            self.model.fit(self.X_train, self.y_train, batch_size=self.params['batch_size'], verbose=0,
                           epochs=self.params['epochs'])
            # predict
            model_evaluation = self.model.evaluate(self.X_test, self.y_test, verbose=0)
            eval_sum += model_evaluation[1] * 100
            self.results.append(model_evaluation[1] * 100)

        return self.get_report()

    def get_report(self):
        results_np = np.array(self.results)
        sumery_dict = dict()
        sumery_dict['mean'] = "%.3f" % results_np.mean() + '%'
        sumery_dict['std'] = "%.3f" % results_np.std() + '%'
        sumery_dict['min'] = "%.3f" % results_np.min() + '%'
        sumery_dict['max'] = "%.3f" % results_np.max() + '%'
        sumery_dict['results'] = str(list(map(lambda x: "%.3f" % x + '%', self.results)))
        return sumery_dict

    def get_model(self):
        return self.model

    def set_first_layer_for_tests(self, layer):
        self.first_layer = layer

    def set_input_dim(self, dim):
        self.input_dim = dim
