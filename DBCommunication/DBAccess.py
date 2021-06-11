# from mongo import Cursor
from pymongo import MongoClient


class Connect(object):
    @staticmethod
    def get_connection():
        username = "eden"
        password = "eden"
        port = 27017
        # url = "mongodb+srv://"+username+":"+password+"@dronescluster.srnyo.mongodb.net"
        # url = "localhost:27017"
        url = "132.72.67.188:27017"
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
    # db.Flights.find({self.param_name: {"$gte": self.min_value, "$lte": self.max_value}})
    min_value = 0
    max_value = 0

    def __init__(self, param_name, min_value, max_value):
        self.param_name = param_name
        self.min_value = min_value
        self.max_value = max_value

    def get_value(self):
        return {"$gte": self.min_value, "$lte": self.max_value}

    # def fetch_from_db(self, db):
    #     return db.Flights.find({self.param_name: {"$gte": self.min_value, "$lte": self.max_value}})


class MinType(ValuesType):
    # return db.Flights.find({self.param_name: {"$gte": self.min_value}})
    min_value = 0

    def __init__(self, param_name, min_value):
        self.param_name = param_name
        self.min_value = min_value

    def get_value(self):
        return {"$gte": self.min_value}

    # def fetch_from_db(self, db):
    #     return db.Flights.find({self.param_name: {"$gte": self.min_value}})


class MaxType(ValuesType):
    #     return db.Flights.find({self.param_name: {"$lte": self.max_value}})
    max_value = 0

    def __init__(self, param_name, max_value):
        self.param_name = param_name
        self.max_value = max_value

    def get_value(self):
        return {"$lte": self.max_value}

    # def fetch_from_db(self, db):
    #     return db.Flights.find({self.param_name: {"$lte": self.max_value}})


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

    # def find_one(self, parameters: dict):
    #     # return self.db.getCollection(collection_name).find_one(data)
    #     return self.flights_collection.find_one(parameters)

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
        return self.db.Jobs.find(parameters)

    def update_job(self, job_identification_details: dict, data_to_update: dict):
        self.db.Jobs.update(job_identification_details, {'$set': data_to_update})

    def job_name_exist(self, parameters: dict):
        cursor = self.fetch_jobs(parameters)
        return cursor.count() >= 1

    def close_conn(self):
        self.mongo_client.close()

    def drop_db(self):
        print(self.mongo_client.list_database_names())
        self.mongo_client.drop_database(self.db_name)
        print(self.mongo_client.list_database_names())
        # self.db.dropDatabase()
        # self.db.Flights.drop()
        # self.db.Jobs.drop()


if __name__ == '__main__':
    # client = MongoClient(
    #     "mongodb+srv://eden:eden@dronescluster.srnyo.mongodb.net")
    # db = client.test_db
    # test_coll = db.test
    # res = test_coll.find_one({'age': 15})
    # test_coll.insert_one({'flie_name':'file', 'age': 30})
    # client.close()
    # # print(res)
    # DBAccess.getInstance().insert_flight({'a': 'sss', 'age': 52})
    # DBAccess.getInstance().insert_flight({'a': 'ede', 'age': 31})
    # DBAccess.getInstance().insert_flight({'a': 'sdfdf', 'age': 50})
    # # print(FlightDBAccess.getInstance().find_one({'age': 18}))
    # # FlightDBAccess.getInstance().insert_user({'username': 'shai', 'pass': 777})
    # # for x in FlightDBAccess.getInstance().get_users({'pass': 777}):
    # #     print(x)
    # [print(x) for x in DBAccess.getInstance().get_flights([])]
    # # range_param = MinType('age',  89)
    # print('-------------')
    # # ks = range_param.fetch_from_db(FlightDBAccess.getInstance().get_db())
    # # [print(x) for x in ks]
    #
    # ls = DBAccess.getInstance().get_flights([MinType('age', 50)])
    # # ls = DBAccess.getInstance().get_flights([MinType('age', 50), SpecificValuesType('weather', ['winter', 'spring', 'summer'])])
    # # ls = FlightDBAccess.getInstance().get_flights([ MinType('age',  89)])
    # [print(x) for x in ls]
    # ls = DBAccess.getInstance().fetch_flights([])
    # print("f")
    # ls = [SpecificValuesType('weather', DBAccess.getInstance().get_flights([]).distinct('weather')), MinType('age',10)]
    # DBAccess.getInstance().insert_job({'job_name': 'sss', 'age': 52})
    # [print(x) for x in DBAccess.getInstance().fetch_jobs({})]
    # print('-------------')
    # DBAccess.getInstance().update_job({'job_name': 'sss'}, {'job_id': 56161516})
    # [print(x) for x in DBAccess.getInstance().fetch_jobs({})]
    # # FlightDBAccess.getInstance().

    # DBAccess.getInstance().insert_flight({'file_name': "AnnaFile", 'data': 123123, 'weather': 'spring', 'age': 30})
    # DBAccess.getInstance().insert_job({'user_email': "anna@com",
    #                                    'job_name_by_user': "first_job",
    #                                    'slurm_job_id': 123,
    #                                    'model_details': {'model_type': 'modelLSTM',
    #                                                      'target_variable': 'weather',
    #                                                      'target_values': ['summer', 'spring'],
    #                                                      'optimizer': 'adam',
    #                                                      'metrics': ['accuracy'],
    #                                                      'iterations': 10,
    #                                                      'batch_size': 5,
    #                                                      'epochs': 8,
    #                                                      'neurons_in_layer': 64,
    #                                                      'report': 'accuracy=80%, loss=0.6'}
    #                                    })
    # DBAccess.getInstance().drop_db()
    [print(x) for x in DBAccess.getInstance().fetch_flights([])]

