from pymongo import MongoClient


class Connect(object):
    @staticmethod
    def get_connection():
        username = "eden"
        password = "eden"
        port = 27017
        # url = "mongodb+srv://"+username+":"+password+"@dronescluster.srnyo.mongodb.net"
        url = "localhost:27017"
        return MongoClient(url)


class ValuesType(object):
    param_name = ""

    def get_name(self):
        return self.param_name


class SpecificValuesType(ValuesType):
    values = list()

    def __init__(self, param_name, values):
        self.param_name = param_name
        self.values = values

    def get_value(self):
        return {'$in': self.values}


class RangeType(ValuesType):
    min_value = 0
    max_value = 0

    def __init__(self, param_name, min_value, max_value):
        self.param_name = param_name
        self.min_value = min_value
        self.max_value = max_value

    def get_value(self):
        return {"$gte": self.min_value, "$lte": self.max_value}


class MinType(ValuesType):
    min_value = 0

    def __init__(self, param_name, min_value):
        self.param_name = param_name
        self.min_value = min_value

    def get_value(self):
        return {"$gte": self.min_value}

class MaxType(ValuesType):
    max_value = 0

    def __init__(self, param_name, max_value):
        self.param_name = param_name
        self.max_value = max_value

    def get_value(self):
        return {"$lte": self.max_value}

class DBAccess:
    db = None
    DB_name = 'flights_db'
    collection_name = 'flights'
    flights_db = None
    flights_collection = None
    __instance = None
    mongo_client = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if DBAccess.__instance == None:
            return DBAccess()
        return DBAccess.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if DBAccess.__instance != None:
            raise Exception("This class is a singleton!")
        else:

            self.mongo_client = Connect().get_connection()
            # Create the jobs and drones flights database under the name 'Jobs_And_Flights_DB'
            self.db = self.mongo_client.Jobs_And_Flights_DB
            self.db_name = "Jobs_And_Flights_DB"
            DBAccess.__instance = self

    def get_db(self):
        return self.db

    def fetch_flight_param_values(self, param_name: str) -> list:
        """
        Returns a list of all the distinct values of parameter param_name, from Flights collection
        :param param_name: parameter's name
        :return:
        """
        return self.fetch_flights([]).distinct(param_name)

    def insert_flight(self, data: dict):
        """ """
        self.db.Flights.insert_one(data)

    def fetch_flights(self, parameters: list):
        """
        :param parameters: [angeValues, MaxValue, MinValue, ...]
        :return: all flights that fulfilled the conditions for each parameter
        """
        params_dict = dict()
        for param in parameters:
            params_dict[param.get_name()] = param.get_value()

        return self.db.Flights.find(params_dict)

    def insert_job(self, data: dict):
        self.db.Jobs.insert_one(data)

    def fetch_jobs(self, parameters: dict):
        """
        :param parameters: dict where the keys are the parameters name and the values are the parameters value
                           Exp: {'Job_id': 123, 'job_name_by_user': 'my job', ...}
        :return: all jobs that fulfilled the conditions for each parameter
        """
        jobs_cursor = self.db.Jobs.find(parameters)
        jobs = []
        for job in jobs_cursor:
            jobs.append(job)
        return jobs

    def update_job(self, job_identification_details: dict, data_to_update: dict):
        self.db.Jobs.update(job_identification_details, {'$set': data_to_update})

    def job_name_exist(self, parameters: dict):
        return len(self.fetch_jobs(parameters)) >= 1

    def close_conn(self):
        self.mongo_client.close()

    def drop_db(self):
        # print(self.mongo_client.list_database_names())
        self.mongo_client.drop_database(self.db_name)
        # print(self.mongo_client.list_database_names())


if __name__ == '__main__':
    pass
