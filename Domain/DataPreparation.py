import csv
import os
import shutil
import sys
from functools import reduce
sys.path.append(os.getcwd().split('\DataPreparation')[0])
from DBCommunication.DBAccess import DBAccess

"""
    This class is responsible for preparing the flights data.
    The prepared data will be saved in a CSV file and will be ready for the CNN model analysis.
"""


class DataPreparation:

    def __init__(self, data_dir_path, file_name, div_num, number_of_features):
        """
        :param data_dir_path: Path to wanted directory, where the csv file will be saved.
        :param file_name: Name of the CSV file. In this file the prepared data will be saved and ready for analysis.
        :param div_num:
        :param number_of_features: number of features
        """

        self.DS_FOLDER = data_dir_path
        self.DATASET_FILE_NAME = file_name
        self.DATASET_FILE_PATH = self.DS_FOLDER + '/' + self.DATASET_FILE_NAME
        self.db = DBAccess.getInstance()
        self.div_num = div_num  # normalize the number to be < 1
        self.NUMBER_OF_FEATURES = number_of_features
        self.NUMBER_OF_VECTORES = 3

    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def feature_padding(self, features: list, padd_size: int):
        """
        Add padding to features - the function add the last x, y, z values to the end of the list - until we got to padd_size
        :param features: list of features
        :param padd_size: number of features to add to the list
        :return:
        """
        if len(features) < 3:
            # print(features)
            raise Exception("feature_padding: features length is too small")

        for i in range(padd_size):
            features += [features[-3]]
        return features

    def fix_features_size(self, features, size):
        """
        Get list of features and size and return a list of the features with length of `size` (by cut \ padd)
        :param features:
        :param size: number of features (120*(x,y,z))
        :return:
        """
        features = features[:size]
        if len(features) < size:
            features = self.feature_padding(features, size - len(features))
        return features

    def create_data_set(self, files_names):
        """
        reading the txt file and parsing it into excel, and normalizing
        :param files_names: list of files names and their folder
        :return:
        """
        all_data = []
        for file in files_names:
            filename = file['file_name']
            folder = file['folder']
            data = []
            save_data = False
            skip_details = False
            with open(os.path.join(self.DS_FOLDER, folder, filename)) as f:
                for line in f.readlines():
                    if not skip_details:
                        skip_details = True
                        continue
                    splited_line = line.split('\t')
                    if line == '\n':
                        continue
                    x_val = splited_line[1]
                    if (self.isfloat(x_val) and float(x_val) != 0.0):
                        save_data = True
                    if (save_data):
                        xyz_data = [str(float(x) / self.div_num) for x in splited_line[1:self.NUMBER_OF_VECTORES + 1]]
                        data += xyz_data  # splited_line[1:4]
            data = self.fix_features_size(data, self.NUMBER_OF_FEATURES)
            # adding the 'point_of_view' field
            data += [folder]
            all_data.append(data)
        return all_data

    def get_csv_with_prepared_data(self, logs_queries: dict, prediction_variable: str, prediction_values: list):
        """
            Creates datasets csv file, each line in the file will be [x1,y1,z1,..., x120, y120, z120, prediction_value]
            get all the files that uphold all the logs queries and create directories according to the prediction values
        :param logs_queries:
        :param prediction_variable: the target variable
        :param prediction_values: list of the optional outputs to the prediction field (label, y)
                (for example: for prediction field 'weather' -> prediction_values = ['summer', 'winter', 'spring'])
        :return: the file's path
        """
        # 1. get data from db
        files_dicts: list = self.db.fetch_flights(logs_queries)
        files_dicts = list(filter(lambda file: prediction_variable in file.keys(), files_dicts))

        # 2. create directories: create a folder per predication value
        for val in prediction_values:
            val = str(val)
            if not os.path.exists(self.DS_FOLDER + "/" + val):
                os.makedirs(self.DS_FOLDER + "/" + val)

            for file in files_dicts:
                if prediction_variable in file.keys() and str(file[prediction_variable]) == val:
                    output_file = open(self.DS_FOLDER + "/" + val + "/" + file['file_name'].strip('log') + "txt", "w")
                    file_keys = list(filter(lambda key: key != '_id' and key != 'data', file.keys()))
                    details = reduce(lambda acc, curr_key: acc + curr_key + '=' + str(file[curr_key]) + ',',
                                     file_keys, "")
                    # print('details:' + details)
                    output_file.write(details + '\n')
                    # output_file.write('TimeStamp' + '\t' + 'POS_X' + '\t' + 'POS_Y' + '\t' + 'POS_Z' + '\n')
                    output_file.write(file['data'] + '\n')
                    output_file.close()

        # 3. get all files in a list from all the directories
        files_names = []
        for __, directories, __ in os.walk(self.DS_FOLDER):
            for directory in directories:
                for __, __, files in os.walk(self.DS_FOLDER + "/" + directory):
                    files_names += list(map(lambda file: {'file_name': file, 'folder': directory}, files))

        dataset = self.create_data_set(files_names)
        header_data = [len(dataset), self.NUMBER_OF_FEATURES] + prediction_values
        dataset.insert(0, header_data)

        # 4. Save the dataset as a CSV file in the wanted structure.
        with open(self.DATASET_FILE_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(dataset)

        # returns the path to the prepared dataset file
        return self.DATASET_FILE_PATH

    def clear_data_folder(self):
        # delete each directory
        if os.path.exists(self.DS_FOLDER):
            for __, directories, __ in os.walk(self.DS_FOLDER):
                [shutil.rmtree(self.DS_FOLDER + "/" + dir) for dir in directories]
