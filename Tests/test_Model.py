from unittest import TestCase

import tensorflow as tf
from pandas import np

from Domain.models.Model import Model


class TestModel(TestCase):
    def setUp(self):
        model_type = 'modelLSTM'
        self.parameters = {'optimizer': "adam",
                           'metrics': ['accuracy'],
                           'iterations': 4,
                           'batch_size': 2,
                           'epochs': 3,
                           'neurons_in_layer': 64}
        self.model = Model(model_type, self.parameters)

    def test_get_parameters(self):
        self.assertEqual(self.model.get_parameters(), [["optimizer", 'str'], ["metrics", 'list'], ["iterations", 'int'],
                                                       ["batch_size", 'int'], ["epochs", 'int'], ["neurons_in_layer", 'int']])

    def test_build_model(self):
        self.assertEqual(self.model.get_model(), None)
        self.model.set_first_layer_for_tests(tf.keras.layers.LSTM(self.parameters['neurons_in_layer'], input_shape=(None, 360)))
        self.model.build_model()
        self.assertNotEqual(self.model.get_model(), None)

    def test_train_and_predict_model(self):
        ndim = 5
        self.model.set_input_dim(ndim)
        feature_of_class1 = [[5, 56, 7, 34, 6]]
        feature_of_class2 = [[6, 3, 89, 45, 83]]
        X_train = np.array([feature_of_class1, feature_of_class1, feature_of_class1, feature_of_class1, feature_of_class1,
                       feature_of_class2, feature_of_class2, feature_of_class2])
        y_train = np.array([0, 0, 0, 0, 0, 1, 1, 1])
        X_test = np.array([feature_of_class1, feature_of_class1, feature_of_class2])
        y_test = np.array([0, 0, 1])
        self.model.set_first_layer_for_tests(tf.keras.layers.LSTM(self.parameters['neurons_in_layer'], input_shape=(None, ndim)))
        self.model.set_output_size(2)
        self.model.set_train_test_sets(X_train, y_train, X_test, y_test)
        report = self.model.train_and_predict_model()
        print(report)
        self.assertTrue(True)

