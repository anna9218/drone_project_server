import json
import os
import sys

from flask import Flask, jsonify, request
# TODO: for downloading flask_cors run this line in terminal: conda install -c anaconda flask_cors
from flask_cors import CORS

sys.path.append(os.getcwd().split('\WebCommunication')[0])
from Domain import FlightsManager
from Domain.JobsManager import JobsManager

app = Flask(__name__)
CORS(app)


@app.route('/upload_flight', methods=['POST'])
def upload_flight():
    file = request.files['file']
    parameters: dict = json.loads(request.form['parameters'])  # gets {'p1': 22, 'p2': 'sss'}
    parameters['location'] = request.form['locationTags']
    response = FlightsManager.upload_flight(file, parameters)
    if response:
        return jsonify(msg=response['msg'], data=response['data'])
    return jsonify(msg='Error - file upload Failure.', data=False)


@app.route('/get_models_types', methods=['GET'])
def get_models_types():
    response = JobsManager().get_models_types()
    return jsonify(msg=response['msg'], data=response['data'])


@app.route('/fetch_parameters', methods=['GET'])
def fetch_parameters():
    response = JobsManager().get_all_parameters()
    if response:
        return jsonify(msg=response['msg'], data=response['data'])
    return jsonify(msg=response['msg'], data=response['data'])


@app.route('/fetch_model_parameters', methods=['POST'])
def fetch_model_parameters():
    model_type = request.form['model_type']
    response = JobsManager().get_model_parameters(model_type)
    if response:
        return jsonify(msg=response['msg'], data=response['data'])
    return jsonify(msg=response['msg'], data=response['data'])


@app.route('/fetch_flight_param_values', methods=['POST'])
def fetch_flight_param_values():
    parameter: str = request.form['parameter']
    try:
        data = JobsManager().fetch_flight_param_values(parameter)
        return jsonify(msg='Parameter\'s values retrieved successfully', data=data)
    except:
        return jsonify(msg='Error with the server', data=[])


@app.route('/run_new_job', methods=['POST'])
def run_new_job():
    job_name_by_user: str = request.form['job_name_by_user']
    user_email: str = request.form['user_email']
    model_type: str = request.form['model_type']
    model_details: dict = json.loads(request.form['model_details'])
    logs_queries: dict = json.loads(request.form['logs_queries'])
    target_variable = request.form['target_variable']
    response = JobsManager().run_new_job(user_email, job_name_by_user, model_type, model_details, logs_queries,
                                         target_variable)
    return response


@app.route('/cancel_job', methods=['POST'])
def cancel_job():
    user_email: str = request.form['user_email']
    slurm_job_id: str = request.form['job_id']
    response = JobsManager().cancel_job(user_email, slurm_job_id)
    if response:
        return jsonify(msg='Job ' + str(slurm_job_id) + ' was canceled successfully!', data=True)
    return jsonify(msg='Error! Job ' + str(slurm_job_id) + ' was not canceled!', data=False)


@app.route('/fetch_researcher_jobs', methods=['POST'])
def fetch_researcher_jobs():
    user_email: str = request.form['user_email']
    try:
        response = JobsManager().fetch_researcher_jobs(user_email)
        return jsonify(msg=response['msg'], data=response['data'])
    except:
        return jsonify(msg='Error with the server', data=[])


if __name__ == '__main__':
    ip = "132.72.67.188"
    port = 8021
    app.run(host=ip, port=port)
