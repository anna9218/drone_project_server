from unittest import TestCase
import os, sys
import mock


sys.path.append(os.getcwd().split('\Tests')[0])
from Tests.StubDBAccess import StubDBAccess


class TestJobsManager(TestCase):

    @mock.patch('SlurmCommunication.SlurmManager.copy_directory_to_gpu_server')
    def setUp(self, mock_copy_directory_to_gpu_server):
        mock_copy_directory_to_gpu_server.return_value = True
        from Domain.JobsManager import JobsManager
        self.manager = JobsManager()
        self.flight1 = {'file_name': 'log1.log', 'weather': 'summer'}
        self.flight2 = {'file_name': 'log2.log', 'weather': 'spring', 'age': 34}
        self.flight3 = {'file_name': 'log3.log', 'weather': 'winter', 'gender': 'male'}

    @mock.patch('SlurmFunctions.models.Model.Model.get_parameters')
    def test_get_model_parameters(self, mock_get_parameters):
        mock_get_parameters.return_value = [{'flle_name': 'log1.log', 'weather': 'summer'}]
        params = ['param1', 'param2']
        mock_get_parameters.return_value = params
        # valid input
        self.assertEqual(self.manager.get_model_parameters('modelDENSE'), {'msg': "Success", 'data': params})
        # invalid input
        self.assertEqual(self.manager.get_model_parameters("NOTHING"),
                         {'msg': "Failure, Error in server(JobsManager.get_model_parameters function)", 'data': []})
        self.assertEqual(self.manager.get_model_parameters(None),
                         {'msg': "Failure, Error in server(JobsManager.get_model_parameters function)", 'data': []})

    @mock.patch('SlurmCommunication.SlurmManager.run_job_on_gpu')
    @mock.patch('SlurmCommunication.SlurmManager.move_file_to_gpu')
    @mock.patch('Domain.DataPreparation.DataPreparation.clear_data_folder')
    @mock.patch('Domain.DataPreparation.DataPreparation.get_csv_with_prepared_data')
    def test_run_new_job(self, mock_get_csv_with_prepared_data, mock_clear_data_folder, mock_move_file_to_gpu, mock_run_job_on_gpu):
        # mock_getInstance.return_value =
        job_id1 = 1234
        job_id2 = 8767
        user_email1_succ = 'succ_someone@gmail.com'
        user_email2_fail = 'fail_someone@gmail.com'
        self.manager.set_db_of_tests(StubDBAccess(job_id1, user_email1_succ, job_id2, user_email2_fail))
        mock_get_csv_with_prepared_data.return_value = '/url'
        mock_move_file_to_gpu.return_value = True
        mock_run_job_on_gpu.return_value = job_id1
        mock_clear_data_folder.return_value = True

        self.assertDictEqual(self.manager.run_new_job(user_email2_fail, 'job_name_by_user', None, None, {}, None),
                             {'msg': "Error, Invalid input.",
                              'data': False})

        mock_run_job_on_gpu.return_value = -1
        self.assertDictEqual(self.manager.run_new_job(user_email1_succ, None, None, None, {}, None),
                             {'msg': "Error, Invalid input.",
                              'data': False})

        mock_run_job_on_gpu.return_value = 6587
        self.assertDictEqual(self.manager.run_new_job(user_email1_succ, 'job_name_by_user', "", dict(), dict(), ""),
                            {'msg': 'Job job_name_by_user was submitted successfully',
                             'data': True})


    @mock.patch('SlurmCommunication.SlurmManager.cancel_job')
    @mock.patch('SlurmCommunication.SlurmManager.get_all_user_jobs')
    def test_cancel_job(self, mock_get_all_user_jobs, mock_cancel_job):
        job_id1 = 1234
        job_id2 = 4566
        job_id3 = 2426
        job_id4 = 6726
        mock_cancel_job.return_value = True
        mock_get_all_user_jobs.return_value = [{'job_id': job_id2, 'state': 'RUNNING'},
                                               {'job_id': job_id1, 'state': 'CANCELLED'},
                                               {'job_id': job_id3, 'state': 'CANCELED'},
                                               {'job_id': job_id4, 'state': 'CANCELLED+'}]
        user_email = 'edenta@bla.com'
        # valid input
        self.assertDictEqual(self.manager.cancel_job(user_email, job_id1),
                             {'msg': "Job " + str(job_id1) + " was canceled successfully", 'data': True})
        self.assertDictEqual(self.manager.cancel_job(user_email, job_id3),
                             {'msg': "Job " + str(job_id3) + " was canceled successfully", 'data': True})
        self.assertDictEqual(self.manager.cancel_job(user_email, job_id4),
                             {'msg': "Job " + str(job_id4) + " was canceled successfully", 'data': True})
        self.assertDictEqual(self.manager.cancel_job(user_email, job_id2),
                             {'msg': "Failure, the job " + str(job_id2) + " wasn't canceled.", 'data': False})
        # invalid input
        self.assertDictEqual(self.manager.cancel_job(user_email, None),
                             {'msg': "Failure, error with the server", 'data': False})
        self.assertDictEqual(self.manager.cancel_job(user_email, 34235),
                             {'msg': "Failure, error with the server", 'data': False})

    @mock.patch('DBCommunication.DBAccess.DBAccess.fetch_flights')
    def test_get_all_parameters(self, mock_fetch_flights):
        # valid inputs
        mock_fetch_flights.return_value = [self.flight1, self.flight2, self.flight3]
        self.assertDictEqual(self.manager.get_all_parameters(),
                             {'data': [['weather', 'str'],
                                       ['age', 'int'],
                                       ['gender', 'str']],
                              'msg': 'Success'})
        mock_fetch_flights.return_value = []
        self.assertDictEqual(self.manager.get_all_parameters(),
                             {'data': [],
                              'msg': 'Success'})
        # invalid inputs
        mock_fetch_flights.return_value = None
        self.assertDictEqual(self.manager.get_all_parameters(),
                             {'data': [],
                              'msg': "Failure, error with the server (JobManager.get_all_parameters)"})

    @mock.patch('os.listdir')
    def test_get_models_types(self, mock_listdir):
        mock_listdir.return_value = ["m1.py", "m2.py"]
        self.assertDictEqual(self.manager.get_models_types(), {'msg': 'Success', 'data': ['m1', 'm2']})

        mock_listdir.return_value = ["m1", "m2.py", "__init__.py"]
        self.assertDictEqual(self.manager.get_models_types(), {'msg': 'Success', 'data': ['m1', 'm2']})

    @mock.patch('SlurmCommunication.SlurmManager.get_all_user_jobs')
    @mock.patch('SlurmCommunication.SlurmManager.get_job_report')
    def test_fetch_researcher_jobs(self, mock_get_job_report, mock_get_all_user_jobs):
        job1_db = {'user_email': 'someone@gmail.com',
                   'job_id': 5346,
                   'job_name_by_user': 'myFirstJob',
                   'start_time': '10:00',
                   'end_time': '11:00',
                   'status': 'COMPLETED',
                   'model_details': {'optimizer': 'adam',
                                     'metrics': ['accuracy'],
                                     'iterations': 4,
                                     'batch_size': 6,
                                     'epochs': 7,
                                     'neurons_in_layer': 65},
                   'report': 'old report'}
        job2_db = {'user_email': 'someone@gmail.com',
                   'job_id': 1234,
                   'job_name_by_user': 'mySecondJob',
                   'model_details': {'optimizer': 'adam',
                                     'metrics': ['accuracy'],
                                     'iterations': 4,
                                     'batch_size': 6,
                                     'epochs': 7,
                                     'neurons_in_layer': 65}}
        job1_gpu = {'job_id': 1234,
                    'start_time': '15:00',
                    'end_time': '16:00',
                    'state': 'COMPLETED'}
        self.manager.set_db_of_tests(StubDBAccess(jobs=[]))

        self.assertDictEqual(self.manager.fetch_researcher_jobs('someone@gmail.com'),
                             {'msg': "You don't have any jobs.",
                              'data': None})
        self.manager.set_db_of_tests(StubDBAccess(jobs=[job1_db, job2_db]))
        mock_get_job_report.return_value = "my report"
        mock_get_all_user_jobs.return_value = []
        self.assertDictEqual(self.manager.fetch_researcher_jobs('someone@gmail.com'),
                             {'msg': "Success",
                              'data': [job1_db, job2_db]})

        updated_job_2 = {'user_email': 'someone@gmail.com',
                         'job_id': 1234,
                         'job_name_by_user': 'mySecondJob',
                         'start_time': '15:00',
                         'end_time': '16:00',
                         'status': 'COMPLETED',
                         'model_details': {'optimizer': 'adam',
                                           'metrics': ['accuracy'],
                                           'iterations': 4,
                                           'batch_size': 6,
                                           'epochs': 7,
                                           'neurons_in_layer': 65},
                         'report': "my report"}
        mock_get_all_user_jobs.return_value = [job1_gpu]
        self.assertDictEqual(self.manager.fetch_researcher_jobs('someone@gmail.com'),
                             {'msg': "Success",
                              'data': [job1_db, updated_job_2]})
