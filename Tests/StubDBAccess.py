from DBCommunication.DBAccess import DBAccess


class StubDBAccess(DBAccess):
    def __init__(self):
        pass

    def getInstance(self):
        return self

    def fetch_flight_param_values(self, param_name: str) -> list:
        pass

    def insert_user(self, data: dict):
        pass

    def fetch_users(self, parameters: dict):
        pass

    def insert_flight(self, data: dict):
        pass

    def fetch_flights(self, parameters: list):
        return [{'file_name': 'log1.log', 'weather': 'summer', 'data': 'TimeStamp\tPOS_X\tPOS_Y\tPOS_Z\n' +
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


    def insert_job(self, data: dict):
        pass

    def fetch_jobs(self, parameters: dict):
        pass

    def update_job(self, job_identification_details: dict, data_to_update: dict):
        pass
