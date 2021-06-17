import os
import subprocess
from collections import defaultdict
from functools import reduce
from sys import stdout

"""
    THIS CLASS IS LOCATED ON THE GPU SERVER (where the slurm software is installed)
"""

users_and_jobs = defaultdict(list)

"""
    Login details:
    for connecting a server with a different user name (on the university servers)
    please change:
        1. user_name_on_university_servers
        2. password
        3. gpu_environment_name (packages that are needed to be installed on conda env are described in maintenance document)
    to your own details.
"""
user_name_on_university_servers = "shao"
password = "shaiOz05"
gpu_environment_name = 'py36'
local_addr = user_name_on_university_servers + "@132.72.67.188"
gpu_addr = user_name_on_university_servers + "@gpu.bgu.ac.il"


directory_of_slurm_functions_on_gpu = 'SlurmFunctions'
run_job_path_on_gpu = directory_of_slurm_functions_on_gpu + '/runJob.py'


def create_sbatch_file(user_email, path_to_python_job_file_to_run, param_list):
    text = ""
    user_name = user_email.split('@')[0]
    file_name = user_name + str(len(users_and_jobs[user_name]) + 1) + "_sbatchFile.txt"

    text += "\'#!/bin/bash \n\n\'"
    text += "\'#SBATCH --partition main \n\'"
    text += "\'#SBATCH --time 0-10:00:00 \n\'"
    text += "\'#SBATCH --job-name " + user_name + str(len(users_and_jobs[user_name]) + 1) + "_job \n\'"
    text += "\'#SBATCH --output job-%J.out \n\'"
    text += "\'#SBATCH --mail-user=" + user_email +" \n\'"
    text += "\'#SBATCH --mail-type=ALL \n\'"
    text += "\'#SBATCH --gres=gpu:1 \n\'"
    text += "\'#SBATCH --mem=32G \n\'"
    text += "\'#SBATCH --cpus-per-task=6 \n\'"
    text += "\'### Print some data to output file ### \n\'"
    text += "\'echo `date` \n\'"
    text += "\'echo -e \"\\nSLURM_JOBID:\\t\\t\" $SLURM_JOBID \n\'"
    text += "\'echo -e \"SLURM_JOB_NODELIST:\\t\" $SLURM_JOB_NODELIST \"\\n\\n\" \n\n\'"
    text += "\'### Start your code below #### \n\'"
    text += "\'module load anaconda \n\'"
    text += "\'source activate " + gpu_environment_name + " \n\'"
    params_as_string = " ".join(param_list)
    text += "\'python " + path_to_python_job_file_to_run + " " + params_as_string + " \n\'"

    exe_cmd_on_gpu_server('echo ' + text + ' > ' + file_name)

    return file_name


def run_job_on_gpu(user_email, path_to_python_job_file_to_run, param_list):
    batch_file_name = create_sbatch_file(user_email, path_to_python_job_file_to_run, param_list)
    user_name = user_email.split('@')[0]
    with open("runJob.txt", "w+") as fout:
        print("file opened, about to call run job")
        cmd = 'python ' + run_job_path_on_gpu + ' ' + batch_file_name
        out = exe_cmd_on_gpu_server(cmd, fout)
        fout.seek(0)
        output = fout.read()
        job_id = output.split()[-1] if "Submitted batch job" in output else -1
        users_and_jobs[user_name].append(job_id)
        print("users_and_jobs: ")
        print(users_and_jobs)
        return job_id


def get_all_user_jobs():
    with open("all_jobs.txt", "w+") as fout:
        cmd = "sacct --format=JobID,JobName,State,Start,End"
        out = exe_cmd_on_gpu_server(cmd, fout)
        fout.seek(0)
        output = fout.read()
        all_jobs_list = output.split('\n')
        if len(all_jobs_list) > 1:
            tmp = all_jobs_list[2:]
            clean_list_of_jobs = []
            for job_row in tmp:
                job_id_with_junk = job_row.split(" ")[0]
                job_id = job_id_with_junk.split(".")
                if len(job_id) == 1:
                    clean_list_of_jobs.append(job_row)
            final_data = []
            for job in clean_list_of_jobs:
                list_of_id_start_end = list(filter(lambda el: el != "", job.split(" ")))
                if len(list_of_id_start_end) > 0:
                    final_data.append(list_of_id_start_end)
            final_data = list(map(lambda el: {"job_id": el[0],
                                              "job_name": el[1],
                                              "state": el[2],
                                              "start_time": el[3],
                                              "end_time": el[4]}, final_data))
            return final_data
        return []


def cancel_job(job_id):
    exe_cmd_on_gpu_server("scancel " + str(job_id))


def exe_cmd_on_gpu_server(cmd, fout=stdout):
    return subprocess.call(["sshpass", "-p", password, "ssh", "-t", gpu_addr,
                            'StrictHostKeyChecking=no; ' + cmd + '; exit'], stdout=fout)


def move_file_to_gpu(source_path, dest_path):
    with open(source_path, "r") as file:
        output = file.readlines()
        output = reduce(lambda acc, curr: acc + str(curr), output)
        cmd = "echo \'" + output + "\' > " + dest_path
        exe_cmd_on_gpu_server(cmd)


def get_job_report(user_email, job_name_by_user):
    """
    report file will be under the name <user_email>_<job_name_by_user>_report.txt
    and will be located in SlurmFunctions/reports directory
    :param user_email: the user's email that submitted the job
    :param job_name_by_user: job's name
    :return: returns the report's content
    """
    user_name = user_email.split('@')[0]
    with open("reportToReturn.txt", "w+") as fout:
        cmd = "cat " + directory_of_slurm_functions_on_gpu + "/reports/" + user_name + "_" + job_name_by_user + "_report.txt"
        out = exe_cmd_on_gpu_server(cmd, fout)
        fout.seek(0)
        return fout.read()


def copy_directory_to_gpu_server():
    path_to_dir = os.getcwd() + "/" + directory_of_slurm_functions_on_gpu
    source_host = local_addr
    dest_host = gpu_addr
    exe_cmd_on_gpu_server("scp -rp " + source_host + ":" + path_to_dir + " "
                          + dest_host + ":/home/" + user_name_on_university_servers + "/")


# Set up the Folder with needed files in the GPU server.
# copy_directory_to_gpu_server(os.getcwd() + "/" + directory_of_slurm_functions_on_gpu)
