from unittest import TestCase
import sys, os
sys.path.append(os.getcwd().split('\Tests')[0])
from DBCommunication.DBAccess import DBAccess


class TestDBAccess(TestCase):
    def setUp(self):
        self.db = DBAccess.getInstance()
        self.db.db = self.db.mongo_client.test_db
        self.db.db_name = "test_db"
        self.db.insert_flight({'file_name': 'file1', 'data': 1234})
        self.db.insert_flight({'file_name': 'file2', 'data': 4567})

        self.db.insert_job({'job_name': "job1", 'user_email': 'bla1@gmail.com'})
        self.db.insert_job({'job_name': "job2", 'user_email': 'bla2@gmail.com'})

    def test_fetch_flight_param_values(self):
        vals = self.db.fetch_flight_param_values('data')
        self.assertTrue(1234 in vals)
        self.assertTrue(4567 in vals)
        self.assertTrue(7890 not in vals)

    def test_insert_flight(self):
        flights = self.db.fetch_flights({})
        flights = list(map(lambda j: j, flights))
        flights[0].pop('_id', None)
        flights[1].pop('_id', None)
        self.assertDictEqual({'file_name': 'file1', 'data': 1234}, flights[0])
        self.assertDictEqual({'file_name': 'file2', 'data': 4567}, flights[1])

    def test_fetch_flights(self):
        flights = self.db.fetch_flights({})
        flights = list(map(lambda j: j, flights))
        flights[0].pop('_id', None)
        flights[1].pop('_id', None)
        self.assertDictEqual({'file_name': 'file1', 'data': 1234}, flights[0])
        self.assertDictEqual({'file_name': 'file2', 'data': 4567}, flights[1])

    def test_insert_job(self):
        jobs = self.db.fetch_jobs({})
        jobs = list(map(lambda j: j, jobs))
        jobs[0].pop('_id', None)
        jobs[1].pop('_id', None)
        self.assertDictEqual({'job_name': "job1", 'user_email': 'bla1@gmail.com'}, jobs[0])
        self.assertDictEqual({'job_name': "job2", 'user_email': 'bla2@gmail.com'}, jobs[1])

    def test_fetch_jobs(self):
        self.db.insert_job({'job_name': "job1", 'user_email': 'bla1@gmail.com'})
        self.db.insert_job({'job_name': "job2", 'user_email': 'bla2@gmail.com'})
        jobs = self.db.fetch_jobs({})
        jobs = list(map(lambda j: j, jobs))
        jobs[0].pop('_id', None)
        jobs[1].pop('_id', None)
        self.assertDictEqual({'job_name': "job1", 'user_email': 'bla1@gmail.com'}, jobs[0])
        self.assertDictEqual({'job_name': "job2", 'user_email': 'bla2@gmail.com'}, jobs[1])


    def test_update_job(self):
        self.db.insert_job({'job_name': "job1"})
        self.db.update_job({'job_name': "job1"}, {'user_email': 'bla1@gmail.com'})
        job = self.db.fetch_jobs({'job_name': 'job1'})[0]
        job.pop('_id', None)
        self.assertDictEqual({'job_name': "job1", 'user_email': 'bla1@gmail.com'}, job)

        self.db.update_job({'job_name': "job2"}, {'user_email': 'bla22@gmail.com'})
        job = self.db.fetch_jobs({'job_name': 'job2'})[0]
        job.pop('_id', None)
        self.assertDictEqual({'job_name': "job2", 'user_email': 'bla22@gmail.com'}, job)

    def test_job_name_exist(self):
        self.db.insert_job({'job_name': "job1"})
        self.assertTrue(self.db.job_name_exist({'job_name': 'job1'}))
        self.assertFalse(self.db.job_name_exist({'job_name': 'job10'}))

    def test_drop_db(self):
        self.db.insert_job({'job_name': "job1"})
        self.assertTrue('test_db' in self.db.mongo_client.list_database_names())
        self.db.drop_db()
        self.assertTrue('test_db' not in self.db.mongo_client.list_database_names())

    def tearDown(self) -> None:
        self.db.drop_db()
