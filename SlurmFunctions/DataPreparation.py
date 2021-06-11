from __future__ import absolute_import, division, unicode_literals
import os
import csv
import shutil
from functools import reduce
import tensorflow as tf
import numpy as np
import sys
sys.path.append(os.getcwd().split('\Domain')[0])

print("TensorFlow version: {}".format(tf.__version__)) # TensorFlow version: 2.3.0
print("Eager execution: {}".format(tf.executing_eagerly()))


class DataPreparation:

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
        features = features.reshape(len(_dataset) - 1, 1, self.NUMBER_OF_FEATURES)  # the -1 is becose the headers line
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
    X_train, y_train, X_test, y_test = DataPreparation().split_to_train_test_from_csv('../data/dataset.csv')
    # print(X_train, y_train, X_test, y_test)
    print(X_train)
    # print(y_train)
    # print(X_test)
    # print(y_test)
    # p: dict = {'model_type': 'model_LSTM',
    #            'optimizer': 'adam',
    #            'metrics': ['accuracy'],
    #            'iterations': 12,
    #            'batch_size': 3,
    #            'epochs': 5,
    #            'neurons_in_layer': 6}
    # x: type = type(['accuracy'])
    # print(x.__name__)
    # print(type(12))
    # print(type('accuracy'))



# from __future__ import absolute_import, division, unicode_literals
# import os
# import csv
# import shutil
# from functools import reduce
# import tensorflow as tf
# import numpy as np
# import sys
# sys.path.append(os.getcwd().split('\Domain')[0])
# from DBCommunication.DBAccess import DBAccess, SpecificValuesType
#
# print("TensorFlow version: {}".format(tf.__version__)) # TensorFlow version: 2.3.0
# print("Eager execution: {}".format(tf.executing_eagerly()))
#
#
# class DataPreparation:
#     DS_FOLDER = "../data"
#     # DS_FOLDER = "./data"
#     NUMBER_OF_VECTORES = 3  #  vector can be "x", "y", "z", "r" (row), "p" (pitch), "y" can also be 7 or 4
#     _NUMBER_OF_POINTS = 120
#     NUMBER_OF_FEATURES = _NUMBER_OF_POINTS * NUMBER_OF_VECTORES  # Sould be multiple of 3 (x, y, z)
#     DATASET_FILE_NAME = "dataset.csv"
#     DATASET_FILE_PATH = DS_FOLDER + "/" + DATASET_FILE_NAME
#     db = DBAccess.getInstance()
#     # CLASS_NAMES = []
#     div_num = 20  # normalize the number to be < 1
#
#     def __init__(self):
#         pass
#
#     def get_csv_with_prepared_data(self, logs_queries: dict, prediction_variable: str, prediction_values: list):
#         """
#         get all the files that uphold all the logs queries and create directories according to the prediction values
#         :param logs_queries:
#         :param prediction_variable:
#         :param prediction_values:
#         :return:
#         """
#         # 1. get data from db
#         files_dicts: list = self.db.fetch_flights(logs_queries)
#         files_dicts = list(filter(lambda file: prediction_variable in file.keys(), files_dicts))
#
#         # 2. create directories: create a folder per predication value
#         for val in prediction_values:
#             if not os.path.exists(self.DS_FOLDER + "/" + val):
#                 os.makedirs(self.DS_FOLDER + "/" + val)
#
#             for file in files_dicts:
#                 if prediction_variable in file.keys() and file[prediction_variable] == val:
#                     output_file = open(self.DS_FOLDER + "/" + val + "/" + file['file_name'].strip('log') + "txt", "w")
#                     file_keys = list(filter(lambda key: key != '_id' and key != 'data', file.keys()))
#                     details = reduce(lambda acc, curr_key: acc + curr_key + '=' + str(file[curr_key]) + ',',
#                                                            file_keys, "")
#                     # print('details:' + details)
#                     output_file.write(details + '\n')
#                     # output_file.write('TimeStamp' + '\t' + 'POS_X' + '\t' + 'POS_Y' + '\t' + 'POS_Z' + '\n')
#                     output_file.write(file['data'] + '\n')
#                     output_file.close()
#         """
#                     Creates datasets csv file, each line in the file will be [x1,y1,z1,..., x120, y120, z120, prediction_value]
#                 :param prediction_values: list of the optional outputs to the prediction field (label, y)
#                         (for example: for prediction field 'weather' -> prediction_values = ['summer', 'winter', 'spring'])
#                 :return: the file's path
#                 """
#         # 3. get all files in a list from all the directories
#         files_names = []
#         for __, directories, __ in os.walk(self.DS_FOLDER):
#             for directory in directories:
#                 for __, __, files in os.walk(self.DS_FOLDER + "/" + directory):
#                     files_names += list(map(lambda file: {'file_name': file, 'folder': directory}, files))
#
#
#         # self.CLASS_NAMES = prediction_values
#
#         dataset = self.create_data_set(files_names)
#         header_data = [len(dataset), self.NUMBER_OF_FEATURES] + prediction_values
#         dataset.insert(0, header_data)
#
#         # self.DATASET_FILE_PATH = self.DS_FOLDER + '/' + self.DATASET_FILE_NAME
#         # 4. Save the dataset as a CSV file in the wanted structure.
#         with open(self.DATASET_FILE_PATH, "w", newline="") as f:
#             writer = csv.writer(f)
#             writer.writerows(dataset)
#
#         # returns the path to the prepared dataset file
#         return self.DATASET_FILE_PATH
#
#     # @staticmethod
#     def clear_data_folder(self):
#         # delete each directory
#         if os.path.exists(self.DS_FOLDER):
#             for __, directories, __ in os.walk(self.DS_FOLDER):
#                 [shutil.rmtree(self.DS_FOLDER + "/" + dir) for dir in directories]
#
#
#     def isfloat(self, value):
#         try:
#             float(value)
#             return True
#         except ValueError:
#             return False
#
#     def feature_padding(self, features: list, padd_size: int):
#         """
#         Add padding to features - the function add the last x, y, z values to the end of the list - until we got to padd_size
#         :param features: list of features
#         :param padd_size: number of features to add to the list
#         :return:
#         """
#         if len(features) < 3:
#             # print(features)
#             raise Exception("feature_padding: features length is too small")
#
#         for i in range(padd_size):
#             features += [features[-3]]
#         return features
#
#     def fix_features_size(self, features, size):
#         """
#         Get list of features and size and return a list of the features with length of `size` (by cut \ padd)
#         :param features:
#         :param size: number of features (120*(x,y,z))
#         :return:
#         """
#         features = features[:size]
#         if len(features) < size:
#             features = self.feature_padding(features, size - len(features))
#         return features
#
#     def create_data_set(self, files_names):
#         """
#         reading the txt file and parsing it into excel, and normalizing
#         :param files_names: list of files names and their folder
#         :return:
#         """
#         all_data = []
#         for file in files_names:
#             filename = file['file_name']
#             folder = file['folder']
#             data = []
#             save_data = False
#             skip_details = False
#             with open(os.path.join(self.DS_FOLDER, folder, filename)) as f:
#                 for line in f.readlines():
#                     if not skip_details:
#                         skip_details = True
#                         continue
#                     splited_line = line.split('\t')
#                     if line == '\n':
#                         continue
#                     x_val = splited_line[1]
#                     if (self.isfloat(x_val) and float(x_val) != 0.0):
#                         save_data = True
#                     if (save_data):
#                         xyz_data = [str(float(x) / self.div_num) for x in splited_line[1:self.NUMBER_OF_VECTORES + 1]]
#                         data += xyz_data  # splited_line[1:4]
#             data = self.fix_features_size(data, self.NUMBER_OF_FEATURES)
#             # adding the 'point_of_view' field
#             data += [folder]
#             all_data.append(data)
#         return all_data
#
#     """## Creating the dataset from the AirSim records"""
#     def create_csv_dataset(self, prediction_values):
#         """
#             Creates datasets csv file, each line in the file will be [x1,y1,z1,..., x120, y120, z120, prediction_value]
#         :param prediction_values: list of the optional outputs to the prediction field (label, y)
#                 (for example: for prediction field 'weather' -> prediction_values = ['summer', 'winter', 'spring'])
#         :return: the file's path
#         """
#         # 1. get all files in a list
#         files_names = []
#         for __, directories, __ in os.walk(self.DS_FOLDER):
#             for directory in directories:
#                 for __, __, files in os.walk(self.DS_FOLDER + "/" + directory):
#                     files_names += list(map(lambda file: {'file_name': file, 'folder': directory}, files))
#                 # delete each directory
#                 if os.path.exists(self.DS_FOLDER + "/" + directory):
#                     shutil.rmtree(self.DS_FOLDER + "/" + directory)
#
#         # self.CLASS_NAMES = prediction_values
#
#         dataset = self.create_data_set(files_names)
#         header_data = [len(dataset),  self.NUMBER_OF_FEATURES] + prediction_values
#         dataset.insert(0, header_data)
#         # Save the dataset as a CSV file in the wanted structure.
#         with open(self.DATASET_FILE_PATH, "w", newline="") as f:
#             writer = csv.writer(f)
#             writer.writerows(dataset)
#         # returns the path to the datasetfile
#         return self.DATASET_FILE_PATH
#         # return dataset
#
#     def split_array_to_features_and_labels(self, _dataset):
#         """
#         split the _dataset to X = features and y= point_of_view (the predicted field)
#         :param _dataset:
#         :return: per flight, returns features (= list of flights (the GPS points))
#         and labels (= list of start location for each flight in features)
#         """
#         my_LSTM_dataset = _dataset[1:]
#         features = []
#         labels = []
#         for sample in my_LSTM_dataset:
#             tmp_features = sample[:-1]
#             tmp_features = [float(i) for i in tmp_features]
#             features += [tmp_features]
#             # labels += [int(float(sample[-1]))]  # we added float() after the int
#             labels += [sample[-1]]  # we added float() after the int
#         labels = np.array(labels)
#         features = np.array(features)
#         features = features.reshape(len(_dataset) - 1, 1, self.NUMBER_OF_FEATURES)  # the -1 is becose the headers line
#         return features, labels
#
#     def split_to_train_and_test_sets_helper(self, features, labels, number_of_features):
#         number_of_all_features, _, _ = features.shape
#         number_of_labels = number_of_all_features - number_of_features
#         labels_to_choose = np.zeros(number_of_all_features)
#
#         X_train = np.zeros(self.NUMBER_OF_FEATURES).reshape(1, 1, 360)
#         y_train = np.array([])
#         X_test = np.zeros(self.NUMBER_OF_FEATURES).reshape(1, 1, 360)
#         y_test = np.array([])
#
#         for i in range(number_of_labels):
#             random_cell = np.random.randint(0, number_of_all_features)
#             while labels_to_choose[random_cell]:
#                 random_cell = np.random.randint(0, number_of_all_features)
#             labels_to_choose[random_cell] = 1
#
#         for i in range(number_of_all_features):
#             if labels_to_choose[i] == 0:
#                 X_train = np.concatenate((X_train, [features[i]]))
#                 y_train = np.concatenate((y_train, [labels[i]]))
#             else:
#                 X_test = np.concatenate((X_test, [features[i]]))
#                 y_test = np.concatenate((y_test, [labels[i]]))
#
#         return X_train[1:], y_train, X_test[1:], y_test
#
#     # @staticmethod
#     def split_to_train_test_from_csv(self, dataset_path):
#         """
#             this function will run by slurm, reads the data_sets and split is to X_train, y_train, X_test, y_test
#         :param dataset_path:
#         :param prediction_values:
#         :return: X_train, y_train, X_test, y_test
#         """
#
#         # create data sets, each line will be [x1,y1,z1,..., x120, y120, z120, prediction_value]
#         # dataset_csv = self.create_csv_dataset(self.NUMBER_OF_FEATURES, self.DATASET_FILE_PATH, prediction_values)
#         dataset_csv = []
#         with open(dataset_path, 'r') as file:
#             dataset_csv.append(file.read())
#         dataset_csv = dataset_csv[0].split('\n')
#         dataset_csv.remove(dataset_csv[len(dataset_csv)-1])
#         dataset_csv = [line.split(',') for line in dataset_csv]
#
#         # convert array to dataset.
#         all_features, all_labels = self.split_array_to_features_and_labels(dataset_csv)
#
#         i = 0
#         prediction_values:list = dataset_csv[0]
#         prediction_values.remove(prediction_values[0])
#         prediction_values.remove(prediction_values[0])
#         numerical_labels = dict()
#         for val in prediction_values:
#             numerical_labels[str(val)] = i
#             i += 1
#
#         # change all the labels (prediction field) to numerical value
#         if len(all_labels) > 0 and type(all_labels[0]) != 'int' and type(all_labels[0]) != 'float':
#             all_labels = [numerical_labels[str(label)] for label in all_labels]
#
#         # split the dataset randomly to training and testing
#         X_train, y_train, X_test, y_test = \
#             self.split_to_train_and_test_sets_helper(all_features, all_labels,
#                                                      number_of_features=int(all_features.shape[0] * 0.8))
#
#         return X_train, y_train, X_test, y_test
#
#
# if __name__ == '__main__':
#     # DataPreparation().create_data_directories({}, 'wethear', ['summer', 'winter', 'spring'])
#     DataPreparation().get_csv_with_prepared_data([SpecificValuesType('weather', ['summer', 'winter', 'spring'])], 'weather', ['summer', 'winter', 'spring'])
#     DataPreparation().clear_data_folder()
#     # path = DataPreparation().create_csv_dataset(['summer', 'winter', 'spring'])
#     X_train, y_train, X_test, y_test = DataPreparation().split_to_train_test_from_csv('../data/dataset.csv')
#     # print(X_train, y_train, X_test, y_test)
#     print(X_train)
#     # print(y_train)
#     # print(X_test)
#     # print(y_test)
#     # p: dict = {'model_type': 'model_LSTM',
#     #            'optimizer': 'adam',
#     #            'metrics': ['accuracy'],
#     #            'iterations': 12,
#     #            'batch_size': 3,
#     #            'epochs': 5,
#     #            'neurons_in_layer': 6}
#     # x: type = type(['accuracy'])
#     # print(x.__name__)
#     # print(type(12))
#     # print(type('accuracy'))
