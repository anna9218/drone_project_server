import os
from DBCommunication.DBAccess import DBAccess


def convert_flight_data_to_uniformed_format(flight_data: list):
    """
        Returns GPS points form log file
    :param flight_data: list of data from log file
    :return:
    """
    flight_data = [x.decode('UTF-8') for x in flight_data]
    flight_data = [x.split(',') for x in flight_data]
    x_index = 0   # Lat
    y_index = 0   # Lng
    z_index = 0   # Alt
    for data in flight_data:
        data = [x.strip() for x in data]
        try:
            gps_index = data.index('GPS')
            x_index = data.index('Lat') - gps_index -1
            y_index = data.index('Lng') - gps_index -1
            z_index = data.index('Alt') - gps_index -1
            break
        except:
            pass
    flight_data = list(filter(lambda x: x[0] == 'GPS', flight_data))
    # get the timestamp and (x, y, z) = (Lat, Lng, Alt)
    GPSs = [[x[0], int(x[1]), float(x[x_index]), float(x[y_index]), float(x[z_index])] for x in flight_data]

    flight_data = 'TimeStamp' + '\t' + 'POS_X' + '\t' + 'POS_Y' + '\t' + 'POS_Z' + '\n'
    for value in GPSs:
        flight_data += str(value[1]) + '\t' + str(value[2]) + '\t' + str(value[3]) + '\t' + str(value[4]) + '\n'

    return flight_data


def upload_flight(file, flight_details=None):
    """
    Add new drone's flight to the DB
    :param file:
    :param flight_details: dict of flight's details
    :return: Failure or Success
    """
    try:
        file.save(file.filename)
        file_name = file.filename
        with open(file_name, mode='rb') as file:
            flight_data = file.readlines()
            file.close()
            flight_details['file_name'] = file_name
            flight_details['data'] = convert_flight_data_to_uniformed_format(flight_data)
            DBAccess.getInstance().insert_flight(flight_details)
            # DBAccess.getInstance().close_conn()
            try:
                os.remove(file_name)
                return True
            except:
                return True
    except:
        return False