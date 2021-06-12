import os
import sys
from jinja2.utils import import_string
from jsonpickle import json

# OUR import

sys.path.append(os.getcwd().split('\Domain')[0])
from DBCommunication.DBAccess import DBAccess, MinType, MaxType, RangeType, SpecificValuesType
from Domain.DataPreparation import DataPreparation
from SlurmCommunication import SlurmManager


class JobsManager:
    NUMBER_OF_FEATURES = 3 * 120    # 120 GPS points, and 3 coordinates for each GPS point (x, y, z) -> 120 *3
    data_preparation = DataPreparation("../data", "dataset.csv", 20, NUMBER_OF_FEATURES)
    db_access = DBAccess.getInstance()
    model = None
    # EXEC_FILE_PATH = 'SlurmFunctions/./slurmExecutableFile.py'
    EXEC_FILE_PATH = 'SlurmFunctions/./slurmExecutableFile.py'
    # EXEC_FILE_PATH = "../SlurmCommunication/SlurmFunctions/slurmExecutableFile.py"
    MODELS_DIR_PATH = "SlurmFunctions.models."
    MODELS_DIR_PATH2 = "./SlurmFunctions/models"
    # MODELS_DIR_PATH = "SlurmCommunication.SlurmFunctions.models."

    def get_model_parameters(self, model_type: str):
        try:
            model = getattr(import_string(self.MODELS_DIR_PATH + model_type), model_type)()
            params = model.get_parameters()
            return {'msg': "Success", 'data': params}
        except:
            return {'msg': "Failure, Error in server(JobsManager.get_model_parameters function)", 'data': []}

    def fetch_flight_param_values(self, param):
        return self.db_access.fetch_flight_param_values(param)

    def object_to_str(self, obj):
        return json.dumps(obj).replace("\"", "\\\"")

    def str_to_object(self, obj):
        return json.loads(obj)

    def run_new_job(self, user_email: str, job_name_by_user: str, model_type: str, model_details: dict,
                    logs_queries: dict, target_variable: str):
        """

        :param user_email:
        :param job_name_by_user: unique job name
        :param model_type:
        :param model_details: { 'optimizer': str,
                                'metrics': list(str),
                                'iterations': int,
                                'batch_size': int,
                                'epochs': int,
                                'neurons_in_layer' : int}
        :param logs_queries: {'age': ['RangeType', min_value, max_value],
                              'date': ['MinType', min_value],
                              'hour': ['MaxType', max_value],...}
        :param target_variable: target variable name
        :param target_values: list of optional values for the target variable
        :return:
        """

        # check if job_name_by_user doesn't exists in the DB (Jobs document)
        if DBAccess.getInstance().job_name_exist({'job_name_by_user': job_name_by_user, 'user_email': user_email}):
            return {'msg': "Job name  " + job_name_by_user + " already exists.\nPlease enter different job name",
                    'data': False}

        logs_queries = [
            MinType(param_name, logs_queries[param_name][1]) if logs_queries[param_name][0] == 'MinType' else
            MaxType(param_name, logs_queries[param_name][1]) if logs_queries[param_name][0] == 'MaxType' else
            SpecificValuesType(param_name, logs_queries[param_name][1:]) if logs_queries[param_name][
                                                                                0] == 'SpecificValuesType' else
            SpecificValuesType(param_name, self.db_access.fetch_flights([]).distinct(param_name)) if
            logs_queries[param_name][0] == 'AllValuesType' else
            RangeType(param_name, logs_queries[param_name][1], logs_queries[param_name][2]) for param_name in
            logs_queries.keys()]
        target_values = self.db_access.fetch_flight_param_values(target_variable)
        output_size = len(target_values)
        dataset_path = self.data_preparation.get_csv_with_prepared_data(logs_queries, target_variable, target_values)

        dest_dataset_path = "/home/shao/SlurmFunctions/dataset.csv"
        # TODO retrun this line
        SlurmManager.move_file_to_gpu(dataset_path, dest_dataset_path)
        self.data_preparation.clear_data_folder()
        # dataset_path = '../data/dataset.csv'
        param_list = ['createAndRunModel', job_name_by_user, model_type, dest_dataset_path, user_email,
                      str(output_size), str(self.NUMBER_OF_FEATURES), self.object_to_str(model_details)]

        # TODO: delete the 2 lines bellow (for testing with anna)
        # from SlurmFunctions import slurmExecutableFile
        # slurmExecutableFile.create_and_run_model(user_email, job_name_by_user, model_type,
        #                                          model_details, dataset_path, output_size, self.NUMBER_OF_FEATURES)
        # from random import random
        # job_id = random()
        # TODO: t - remove comments from the 1 lines bellow -- call slurm
        job_id = SlurmManager.run_job_on_gpu(user_email, self.EXEC_FILE_PATH, param_list)

        print("job ID is: " + str(job_id))
        if job_id == -1:
            return {'msg': 'Error with Slurm server connection.\nCouldn\'t submit job.', 'data': False}
        # save job to db
        try:
            model_details['model_type'] = model_type
            model_details['target_variable'] = target_variable
            model_details['target_values'] = target_values
            self.db_access.insert_job({'user_email': user_email,
                                       'job_name_by_user': job_name_by_user,
                                       'job_id': job_id,
                                       'model_details': model_details})
        except:
            return {'msg': 'Error with saving job in DB.\nCouldn\'t submit job.', 'data': False}

        return {'msg': 'Job ' + job_name_by_user + ' was submitted successfully', 'data': True}
        # self.db_access.update_job({'job_name_by_user': job_name_by_user}, {'slurm_job_id': job_id})

        # X_train, y_train, X_test, y_test = self.data_preparation.split_to_train_test_from_csv(path)
        # # self.data_preparation.create_csv_dataset(self.NUMBER_OF_FEATURES, self.DATASET_FILE_PATH, prediction_values)
        # # X_train, y_train, X_test, y_test = self.data_preparation.prepare_data(prediction_variable, prediction_values)
        # new_model = model(model_class, {'optimizer': optimizer,
        #                                 'metrics': metrics,
        #                                 'iterations': iterations,
        #                                 'batch_size': batch_size,
        #                                 'epochs': epochs,
        #                                 'neurons_in_layer': neurons_in_layer})
        # new_model.set_train_test_sets(X_train, y_train, X_test, y_test)
        # results = new_model.train_model()
        # print(results)
        # return results
        # _input_dim = 360  # 360 is the number of features, size of input. 3*120 [3 is xyz, 120 is samples during the flight].
        # # 3 layers in each model, last one is dense
        # _units = 64  # num of neurons, going to change
        # _output_size = 4  # labels are from 0 to 9
        # neurons_in_layer = 124
        # optimizer = 'adam'
        # # batch_sizes = [24, 30]
        # batch_size = 24
        # # epochss = [3, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 33, 36]
        # epochs = 3
        # metrics = ['accuracy']
        # iterations = 10
        #
        # # this for loop can be maybe in the reports
        # self.calc_generic_model_average_succes(_input_dim, all_features, all_labels, optimizer, metrics,
        #                                        _output_size, iterations,
        #                                        batch_size, epochs, "LSTM", neurons_in_layer,
        #                                        verbose=0)


    def cancel_job(self, user_email, slurm_job_id):
        # TODO: to test
        try:
            SlurmManager.cancel_job(slurm_job_id)
            canceled_jobs = SlurmManager.get_user_canceled_jobs(user_email)
            canceled_jobs = list(filter(lambda job: canceled_jobs.split(" ")[0], canceled_jobs))
            if slurm_job_id in canceled_jobs:
                return {'msg': "Job " + slurm_job_id + "wasn't canceled successfully", 'data': True}
            else:
                return {'msg': "Failure, the job " + slurm_job_id + "wasn't canceled.", 'data': False}
        except:
            return {'msg': "Failure, error with the server", 'data': False}

    def get_all_parameters(self) -> dict:
        """
        :return: list of all parameters from all the flights in the DB
        """
        try:
            flights = self.db_access.fetch_flights([])
            flights_params = []
            for flight in flights:
                tmp_params = [[key, type(flight[key]).__name__] for key in flight.keys()]
                flights_params += list(filter(lambda param_details: param_details[0] not in ['data', 'file_name', '_id']
                                              and param_details not in flights_params, tmp_params))
            return {'msg': "Success", 'data': flights_params}
        except:
            return {'msg': "Failure, error with the server (JobManager.get_all_parameters)", 'data': []}

    def get_models_types(self):
        """
        Returns list of models names that are in folder "Domain1/models/"
        :return: example for return result = ["modelLSTM", "modelGRU", "modelDENSE"]
        """
        # TODO: the line bellow works on the university's server
        # models: list = os.listdir(self.MODELS_DIR_PATH2)
        # TODO: the line bellow works on the our personal computers
        models: list = os.listdir('../SlurmFunctions/models')
        models = list(map(lambda name: name.split(".")[0], models))
        models = list(filter(lambda name: name not in ['Model', '__init__', '__pycache__'], models))
        return {'msg': "Success", 'data': models}

    def fetch_researcher_jobs(self, user_email: str):
        """
        Returns all the user's jobs with detail from slurm (JobID JobName Partition Account AllocCPUS State ExitCode)
        and details from the DB ('user_email', 'job_name_by_user', 'model_details', reports}).
        Each job will be as follow:
        {'user_email': 'someone@gmail.com'
         'job_id': '001',
         'job_name_by_user': myFirstJob
         'start_time': '10:00',
         'end_time': '11:00',
         'status': 'COMPLETED',
         'model_details': {'optimizer': str,
                           'metrics': list(str),
                           'iterations': int,
                           'batch_size': int,
                           'epochs': int,
                           'neurons_in_layer': int,
                           '}}
         'report': {accuracy: 80, loss: 0.43}}
        """
        # TODO: 2. check the keys in each dict
        # SlurmManager.get_job_report(user_email, job_name_by_user) this function return's content (string) of the report

        # get jobs details from GPU server (slurm)
        jobs_gpu: list = SlurmManager.get_all_user_jobs(user_email)
        print("jobs_gpu : ")
        print(jobs_gpu)
        # get all user's jobs from db
        jobs_db = DBAccess.getInstance().fetch_jobs({"user_email": user_email})
        jobs_to_display = []
        # check if updates are needed for user's jobs
        if len(jobs_db) == 0 and len(jobs_gpu) == 0:
            return {'msg': "You don't have any jobs.", 'data': None}
        for job in jobs_db:
            # if job had report in db -> the job has already updated entirely
            if 'report' in job.keys():
                jobs_to_display.append(job)
                continue
            job_gpu_details = list(filter(lambda j: j['job_id'] == job['job_id'], jobs_gpu))[0]
            if job_gpu_details['state'] == 'COMPLETED':
                job_gpu_details['report'] = SlurmManager.get_job_report(user_email, job['job_name_by_user'])
            # update job details in db
            DBAccess.getInstance().update_job({'job_name_by_user': job['job_name_by_user'], 'user_email': user_email}, job_gpu_details)

            # combine the 2 job dicts
            jobs_to_display.append(job | job_gpu_details)

        return {'msg': "Success", 'data': jobs_to_display}



        # # get jobs details from slurm
        # jobs_details: list = SlurmManager.check_all_user_jobs(user_email)
        # # jobs_details[i] = "JobID JobName Partition Account AllocCPUS State ExitCode"
        # jobs_details = list(map(lambda job: job.split(" "), jobs_details))
        # jobs_dicts: list = []
        # for job in jobs_details:
        #     jobs_dicts.append({"job_id": job[0], "JobName": job[1], "Partition": job[2], "Account": job[3],
        #                        "AllocCPUS": job[4], "status": job[5], "ExitCode": job[6]})
        # jobs_model_details = DBAccess.getInstance().fetch_jobs({"user_email": user_email})
        #
        # if len(jobs_details) == 0 and len(jobs_model_details) == 0:
        #     return {'msg': "You don'd have any jobs.", 'data': []}
        # jobs_start_and_end_times = SlurmManager.get_start_and_end_time(user_email)
        # for job in jobs_dicts:
        #     job_additional_details: dict = list(filter(lambda j: j["slurm_job_id"] == job["job_id"], jobs_model_details))[0]
        #     job_start_and_end_time: dict = list(filter(lambda j: j["JobID"] == job["job_id"], jobs_start_and_end_times))[0]
        #     # a= list(map(lambda key: job[key] = additional_details[key] ,additional_details.keys()))
        #     for key in job_additional_details.keys():
        #         job[key] = job_additional_details[key]
        #     for key in job_start_and_end_time.keys():
        #         if key != "JobID":
        #             job[key] = job_start_and_end_time[key]
        # return {'msg': "Success", 'data': jobs_dicts}


if __name__ == '__main__':
    # SchedulerManager().run_job("modelLSTM", None, None, None, None)
    # print(JobsManager().get_models_types())
    # logs_queries = {'age': ['RangeType', 80, 91], 'weather': ['AllValuesType']}
    logs_queries = {'weather': ['AllValuesType']}
    p: dict = {'model_type': 'model_LSTM',
               'optimizer': 'adam',
               'metrics': ['accuracy'],
               'iterations': 6,
               'batch_size': 24,
               'epochs': 5,
               'neurons_in_layer': 64}

    # JobsManager().run_new_job("eden@gmail.c","eden_job","modelLSTM", p, logs_queries, "weather")

    # import tensorflow as tf
    # # print(JobsManager().get_model_parameters('modelLSTM'))
    # model = tf.keras.models.Sequential([
    #     tf.keras.layers.LSTM(64, input_shape=(None, 360)),
    #     tf.keras.layers.BatchNormalization(),
    #     tf.keras.layers.Dense(3)]
    # )
    # model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    #                    optimizer='adam',
    #                    metrics=['accuracy'])

    print(type(str(p)))
    print((json.dumps(p)))
    x = json.dumps(p)
    print(x.replace("\"", "\\\""))
    print(type(p))
    # txt = json.dumps(p)
    # print(json.loads(txt))
    # print(type(['accuracy']))
