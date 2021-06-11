from __future__ import absolute_import, division, unicode_literals
import os
import numpy as np
import sys
# sys.path.append(os.getcwd().split('\SlurmFunctions')[0])


class SplitData:

    def __init__(self, number_of_features):
        self.NUMBER_OF_FEATURES = number_of_features

    def split_array_to_features_and_labels(self, _dataset):
        """
        split the _dataset to X = features and y= point_of_view (the predicted field)
        :param _dataset:
        :return: per flight, returns features (= list of flights (the GPS points))
        and labels (= list of start location for each flight in features)
        """
        my_LSTM_dataset = _dataset[1:]
        features = []
        labels = []
        for sample in my_LSTM_dataset:
            tmp_features = sample[:-1]
            tmp_features = [float(i) for i in tmp_features]
            features += [tmp_features]
            # labels += [int(float(sample[-1]))]  # we added float() after the int
            labels += [sample[-1]]  # we added float() after the int
        labels = np.array(labels)
        features = np.array(features)
        print(len(_dataset))
        features = features.reshape(len(_dataset) - 1, 1, self.NUMBER_OF_FEATURES)  # the -1 is because the headers line
        return features, labels

    def split_to_train_and_test_sets_helper(self, features, labels, number_of_features):
        number_of_all_features, _, _ = features.shape
        number_of_labels = number_of_all_features - number_of_features
        labels_to_choose = np.zeros(number_of_all_features)

        X_train = np.zeros(self.NUMBER_OF_FEATURES).reshape(1, 1, 360)
        y_train = np.array([])
        X_test = np.zeros(self.NUMBER_OF_FEATURES).reshape(1, 1, 360)
        y_test = np.array([])

        for i in range(number_of_labels):
            random_cell = np.random.randint(0, number_of_all_features)
            while labels_to_choose[random_cell]:
                random_cell = np.random.randint(0, number_of_all_features)
            labels_to_choose[random_cell] = 1

        for i in range(number_of_all_features):
            if labels_to_choose[i] == 0:
                X_train = np.concatenate((X_train, [features[i]]))
                y_train = np.concatenate((y_train, [labels[i]]))
            else:
                X_test = np.concatenate((X_test, [features[i]]))
                y_test = np.concatenate((y_test, [labels[i]]))

        return X_train[1:], y_train, X_test[1:], y_test

    # @staticmethod
    def split_to_train_test_from_csv(self, dataset_path):
        """
            this function will run by slurm, reads the data_sets and split is to X_train, y_train, X_test, y_test
        :param dataset_path:
        :param prediction_values:
        :return: X_train, y_train, X_test, y_test
        """

        # create data sets, each line will be [x1,y1,z1,..., x120, y120, z120, prediction_value]
        # dataset_csv = self.create_csv_dataset(self.NUMBER_OF_FEATURES, self.DATASET_FILE_PATH, prediction_values)
        dataset_csv = []
        with open(dataset_path, 'r') as file:
            dataset_csv.append(file.read())
        dataset_csv = dataset_csv[0].split('\n')
        dataset_csv.remove(dataset_csv[len(dataset_csv)-1])
        dataset_csv = [line.split(',') for line in dataset_csv]

        # convert array to dataset.
        all_features, all_labels = self.split_array_to_features_and_labels(dataset_csv)

        i = 0
        prediction_values: list = dataset_csv[0]
        prediction_values.remove(prediction_values[0])
        prediction_values.remove(prediction_values[0])
        numerical_labels = dict()
        for val in prediction_values:
            numerical_labels[str(val)] = i
            i += 1

        # change all the labels (prediction field) to numerical value
        if len(all_labels) > 0 and type(all_labels[0]) != 'int' and type(all_labels[0]) != 'float':
            all_labels = [numerical_labels[str(label)] for label in all_labels]

        # split the dataset randomly to training and testing
        X_train, y_train, X_test, y_test = \
            self.split_to_train_and_test_sets_helper(all_features, all_labels,
                                                     number_of_features=int(all_features.shape[0] * 0.8))

        return X_train, y_train, X_test, y_test


if __name__ == '__main__':
    # path = DataPreparation().create_csv_dataset(['summer', 'winter', 'spring'])
    # X_train, y_train, X_test, y_test = DataPreparation().split_to_train_test_from_csv('../data/dataset.csv')
    # print(X_train, y
    pass