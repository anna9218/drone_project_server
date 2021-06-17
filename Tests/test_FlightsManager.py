import os
import sys
from unittest import TestCase
from werkzeug.datastructures import FileStorage
sys.path.append(os.getcwd().split('\Tests')[0])
from Domain import FlightsManager
import mock



class TestUniformedFormat(TestCase):

    def setUp(self):
        self.data_with_GPS_point = (open("TestData/2021-01-08 17-17-25.log", 'rb')).readlines()
        self.data_without_GPS_point = []

    def test_convert_flight_data_to_uniformed_format(self):
        result1 = FlightsManager.convert_flight_data_to_uniformed_format(self.data_without_GPS_point)
        result2 = FlightsManager.convert_flight_data_to_uniformed_format(self.data_with_GPS_point)
        self.assertEqual(result1, 'TimeStamp\tPOS_X\tPOS_Y\tPOS_Z\n')
        self.assertEqual(result2, 'TimeStamp\tPOS_X\tPOS_Y\tPOS_Z\n' +
                                  '1627013934	-35.3631754	149.1651923	590.75\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n' +
                                  '189828205	-35.3632443	149.1652301	584.1\n')


class TestUploadFlight(TestCase):

    def setUp(self):
        self.log_file_loc = "TestData/2021-01-07 15-59-47.log"
        self.log_file_copy = open(self.log_file_loc, 'rb')
        self.log_file_storage = FileStorage(self.log_file_copy)
        self.log_file_storage.save(dst=self.log_file_loc)
        self.log_file_copy.close()
        self.log_file = open(self.log_file_loc, 'rb')
        self.log_file = FileStorage(self.log_file)

        self.text_file_name = 'text_file.txt'
        self.text_file = open("text_file.txt", "w+")
        self.text_file.write("This is a text file an not a log file.")
        self.text_file.close()

    @mock.patch('Domain.FlightsManager.convert_flight_data_to_uniformed_format')
    @mock.patch('DBCommunication.DBAccess.DBAccess')
    def test_valid_input(self, mock_db, mock_convert_flight_data_to_uniformed_format):
        mock_db.return_value = True
        # invalid inut
        self.assertDictEqual(FlightsManager.upload_flight(None, {}),
                             {'msg': "Failure, error with the server", 'data': False})
        self.assertDictEqual(FlightsManager.upload_flight(self.log_file, "string is invalid input"),
                             {'msg': "Failure, error with the server", 'data': False})

        # valid input
        mock_convert_flight_data_to_uniformed_format.return_value = ""
        self.assertDictEqual(FlightsManager.upload_flight(self.log_file, {}),
                             {'msg': "Failure, error with the server", 'data': False})
        mock_convert_flight_data_to_uniformed_format.return_value = "12 34 554\n 42 54 65"
        self.assertDictEqual(FlightsManager.upload_flight(self.log_file, {'location': 'summer'}),
                             {'msg': "File uploaded successfully.", 'data': True})


    @mock.patch('DBCommunication.DBAccess.DBAccess')
    def test_invalid_input(self, mock_db):
        mock_db.return_value = True
        self.assertDictEqual(FlightsManager.upload_flight(None, {}), {'msg': 'Failure, error with the server', 'data': False})
        self.assertDictEqual(FlightsManager.upload_flight(self.text_file, {}), {'msg': 'Failure, error with the server', 'data': False})
        self.assertDictEqual(FlightsManager.upload_flight(self.log_file, None), {'msg': 'Failure, error with the server', 'data': False})

    def tearDown(self):
        if os.path.exists(self.text_file_name):
            os.remove(self.text_file_name)
