from unittest import TestCase

import mock

from Domain.JobsManager import JobsManager


class TestJobsManager(TestCase):
    def setUp(self):
        self.manager = JobsManager()

    @mock.patch('Domain1.models.Model.Model.get_parameters')
    def test_get_model_parameters(self, mock_get_parameters):
        params = ['param1', 'param2']
        mock_get_parameters.return_value = params
        self.assertEqual(self.manager.get_model_parameters('modelDENSE'), {'msg': "Success", 'data': params})

    def test_register_researcher(self):
        self.fail()

    def test_valid_login(self):
        self.fail()

    def test_object_to_str(self):
        self.fail()

    def test_str_to_object(self):
        self.fail()

    def test_run_new_job(self):
        self.fail()

    def test_cancel_job(self):
        self.fail()

    def test_get_all_parameters(self):
        self.fail()

    def test_get_models_types(self):
        self.fail()

    def test_fetch_researcher_jobs(self):
        self.fail()
