from DBCommunication.DBAccess import DBAccess


class StubDBAccess(DBAccess):
    def __init__(self, succ_job_name_by_user=None, succ_user_email=None, fail_job_name_by_user=None, fail_user_email=None, jobs=None):
        self.files = [{'file_name': 'log1.log', 'weather': 'summer', 'data': 'TimeStamp\tPOS_X\tPOS_Y\tPOS_Z\n' +
                                                                       '1627013934	-35	149	590\n' +
                                                                       '1627013934	-35	149	590\n' +
                                                                       '1627013934	-35	149	590\n'},
                {'file_name': 'log2.log', 'weather': 'winter', 'data': 'TimeStamp\tPOS_X\tPOS_Y\tPOS_Z\n' +
                                                                       '1627013934	-35	149	590\n' +
                                                                       '1627013934	-35	149	590\n' +
                                                                       '1627013934	-35	149	590\n'},
                {'file_name': 'log3.log', 'weather': 'spring', 'data': 'TimeStamp\tPOS_X\tPOS_Y\tPOS_Z\n' +
                                                                       '1627013934	-35	149	590\n' +
                                                                       '1627013934	-35	149	590\n' +
                                                                       '1627013934	-35	149	590\n'}]
        self.jobs = jobs
        self.succ_job_name_by_user = succ_job_name_by_user
        self.succ_user_email = succ_user_email
        self.fail_job_name_by_user = fail_job_name_by_user
        self.fail_user_email = fail_user_email

    def getInstance(self):
        return self

    def job_name_exist(self, parameters: dict):
        if parameters['job_name_by_user'] == self.fail_job_name_by_user or self.fail_user_email == parameters['user_email']:
            return True
        return False

    def fetch_flight_param_values(self, param_name: str) -> list:
        return list(map(lambda file: file['weather'], self.files))

    def insert_user(self, data: dict):
        pass

    def fetch_users(self, parameters: dict):
        pass

    def insert_flight(self, data: dict):
        pass

    def fetch_flights(self, parameters: list):
        return self.files

    def insert_job(self, data: dict):
        pass

    def fetch_jobs(self, parameters: dict):
        return self.jobs

    def update_job(self, job_identification_details: dict, data_to_update: dict):
        pass
