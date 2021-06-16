from unittest import TestCase
import sys, os
sys.path.append(os.getcwd().split('\Tests')[0])
from SlurmFunctions.SplitData import SplitData


class Test(TestCase):

    def setUp(self):
        self.spltData = SplitData(360)

    def test_split_array_to_features_and_labels(self):
        # valid input
        self.spltData = SplitData(4)
        features, labels = self.spltData.split_array_to_features_and_labels([['first', 'line', 'of', 'data'],
                                                                       [1, 2, 3, 4, 'label1'],
                                                                       [6, 7, 8, 9, 'label2']])
        self.assertEqual(features.shape, (2, 1, 4))
        self.assertEqual(labels.shape, (2,))
        # self.assertEqual(features,)
        for f in features[0][0]:
            self.assertTrue(f in [1., 2., 3., 4.])
        for f in features[1][0]:
            self.assertTrue(f in [6., 7., 8., 9.])
        for l in labels:
            self.assertTrue(l in ['label1', 'label2'])

        # invalid input
        features, labels = self.spltData.split_array_to_features_and_labels([[1, 2, 3, 4, 'label1'],
                                                                             [6, 7, 8, 9, 'label2']])
        self.assertEqual(features.shape, (1, 1, 4))
        self.assertEqual(labels.shape, (1,))
        for f in features[0][0]:
            self.assertTrue(f in [6., 7., 8., 9.])
        for l in labels:
            self.assertTrue(l in ['label2'])

    def test_split_to_train_test_from_csv(self):
        dataset_path = './TestData/dataset.csv'
        X_train, y_train, X_test, y_test = self.spltData.split_to_train_test_from_csv(dataset_path)
        self.assertEqual(X_train.shape, (4, 1, 360))
        self.assertEqual(y_train.shape, (4,))
        self.assertEqual(X_test.shape, (1, 1, 360))
        self.assertEqual(y_test.shape, (1,))

        # invalid input
        try:
            self.spltData.split_to_train_test_from_csv("")
            self.fail()
        except:
            self.assertTrue(True)
        try:
            self.spltData.split_to_train_test_from_csv("bla bla bla\n1 2")
            self.fail()
        except:
            self.assertTrue(True)

