import os
import subprocess
from collections import defaultdict
import time
from sys import stdout

"""
    THIS CLASS IS LOCATED ON THE GPU SERVER (where the slurm software is installed)
    
"""

users_and_jobs = defaultdict(list)
gpu_addr = "shao@gpu.bgu.ac.il"
gpu_pass = "shaiOz05"
directory_of_slurm_functions_on_gpu = 'SlurmFunctions'
run_job_path_on_gpu = directory_of_slurm_functions_on_gpu + '/runJob.py'



def create_sbatch_file(user_email, path_to_python_job_file_to_run, param_list):
    text = ""
    user_name = user_email.split('@')[0]
    file_name = user_name + str(len(users_and_jobs[user_name]) + 1) + "_sbatchFile.txt"

    text += "\'#!/bin/bash \n\n\'"
    text += "\'#SBATCH --partition main \n\'"
    text += "\'#SBATCH --time 0-10:00:00 \n\'"
    text += "\'#SBATCH --job-name "+user_name+str(len(users_and_jobs[user_name]) + 1)+"_job \n\'"
    text += "\'#SBATCH --output job-%J.out \n\'"
    text += "\'#SBATCH --mail-user="+user_email+" \n\'"
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
    # !!!!! maybe change env to py36
    text += "\'source activate projenv \n\'"
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
        print("run job called on gpu")
        fout.seek(0)
        output = fout.read()
        print("output of our server after run job on gpu: "+output)
        job_id = output.split()[-1] if "Submitted batch job" in output else -1
        users_and_jobs[user_name].append(job_id)
        print("job id: "+str(job_id))
        print("users_and_jobs: ")
        print(users_and_jobs)
        return job_id


def check_all_user_jobs(user_email):
    username = user_email.split('@')[0]
    with open("all_jobs.txt", "w+") as fout:
        out = exe_cmd_on_gpu_server("sacct", fout)
        fout.seek(0)
        output = fout.read()
        all_jobs_list = output.split('\n')
        user_jobs = []
        # all_jobs_list[0] = "JobID, JobName, Partition, Account, AllocCPUS, State, ExitCode"
        # all_jobs_list[1] = "-----, -------, ---------, -------, ---------, -----, --------"
        # if len(all_jobs_list) > 1:
        #     user_jobs.append(all_jobs_list[0])
        #     user_jobs.append(all_jobs_list[1])
        for job_row in all_jobs_list:
            if username in job_row:
                user_jobs.append(job_row)
        return user_jobs


def get_start_and_end_time(user_email):
    user_name = user_email.split('@')[0]
    with open(user_name + "StartAndEndTimes.txt", "w+") as fout:
        cmd = "sacct -u " + user_name + " --format=JobID,Start,End"
        out = exe_cmd_on_gpu_server(cmd, fout)
        # out = subprocess.call(["sacct", "-u", user_name, "--format=JobID,Start,End"], stdout=fout)
        fout.seek(0)
        output = fout.read()
        all_jobs_list = output.split('\n')
        if len(all_jobs_list) > 1:
            tmp = all_jobs_list[2:]
            final_list_of_jobs = []
            for job_row in tmp:
                job_id_with_junk = job_row.split(" ")[0]
                job_id = job_id_with_junk.split(".")
                if len(job_id) == 1:
                    final_list_of_jobs.append(job_row)
            final_data = []
            for job in final_list_of_jobs:
                list_of_id_start_end = list(filter(lambda el: el != "", job.split(" ")))
                if len(list_of_id_start_end) > 0:
                    final_data.append(list_of_id_start_end)
            final_data = list(map(lambda el: {"JobId": el[0],
                                              "StartTime": el[1],
                                              "EndTime": el[2]}, final_data))
            # subprocess.call(["rm", user_name + "StartAndEndTimes.txt"])
            return final_data
        return []


def cancel_job(job_id):
    exe_cmd_on_gpu_server("scancel " + str(job_id))


def get_user_jobs_by_state(user_email, state):
    user_name = user_email.split('@')[0]
    curr_user_jobs_list = check_all_user_jobs(user_name)
    list_to_return = []
    for jb in curr_user_jobs_list:
        if state in jb:
            list_to_return.append(jb)
    return list_to_return


def get_user_canceled_jobs(user_email):
    user_name = user_email.split('@')[0]
    return get_user_jobs_by_state(user_name, "CANCELLED") + get_user_jobs_by_state(user_name, "CANCELLED+")


def get_user_completed_jobs(user_email):
    user_name = user_email.split('@')[0]
    return get_user_jobs_by_state(user_name, "COMPLETED")


def get_user_failed_jobs(user_email):
    user_name = user_email.split('@')[0]
    return get_user_jobs_by_state(user_name, "FAILED")


def get_user_pending_jobs(user_email):
    user_name = user_email.split('@')[0]
    return get_user_jobs_by_state(user_name, "PENDING")


def get_user_running_jobs(user_email):
    user_name = user_email.split('@')[0]
    return get_user_jobs_by_state(user_name, "RUNNING")


def get_user_timeout_jobs(user_email):
    user_name = user_email.split('@')[0]
    return get_user_jobs_by_state(user_name, "TIMEOUT")


def check_if_status_changed(job_id):
    with open("job_status.txt", "w+") as fout:
        cmd = "sacct -j " + job_id + " --format=State"
        out = exe_cmd_on_gpu_server(cmd, fout)
        # out = subprocess.call(["sacct", "-j", job_id, "--format=State"], stdout=fout)
        fout.seek(0)
        output = fout.read()
        state_list = output.split('\n')
        # state_list[0] = "State"
        # state_list[1] = "-----"
        if len(state_list) > 1:
            return state_list[2]
        return ""


def exe_cmd_on_gpu_server(cmd, fout=stdout):
    return subprocess.call(["sshpass", "-p", gpu_pass, "ssh", "-t", gpu_addr,
                            'StrictHostKeyChecking=no; conda activate py36; ' + cmd + '; exit'], stdout=fout)


# from subprocess import Popen, PIPE
# import subprocess
def copy_directory_to_gpu_server(path_to_dir):
    # cmd = "scp -rp shao@132.72.67.188:" + path_to_dir + " shao@gpu.bgu.ac.il:/home/shao/"
    # subprocess.call(["sshpass", "-p", gpu_pass, "ssh", "-t", gpu_addr,
    #                  'StrictHostKeyChecking=no; ' + cmd + '; exit'])
    # # subprocess.call(["scp", "-rp", gpu_pass, "ssh", "-t", gpu_addr, 'StrictHostKeyChecking=no; '+cmd+';exit'])
    source_host = "shao@132.72.67.188"
    dest_host = gpu_addr
    exe_cmd_on_gpu_server("scp -rp shao@132.72.67.188:" + path_to_dir + " shao@gpu.bgu.ac.il:/home/shao/")


# Set up the Folder with needed files in the GPU server.
copy_directory_to_gpu_server(os.getcwd() + "/SlurmCommunication/SlurmFunctions")



from subprocess import Popen, PIPE

# import subprocess
if __name__ == "__main__":
    copy_directory_to_gpu_server("/home/shao/testSlurm/DirToCopy")

    # subprocess.call(["scp", "shao@132.72.67.188:fileToSend.txt", "checkingSSH/"])

    # run_job_on_gpu('shao@bgu.ac.il', 'SlurmFunctions/./main.py', ['6000'])
    # TODO for eden:
    # run_job_on_gpu('shao@bgu.ac.il', ''SlurmFunctions/./slurmExecutableFile.py', ['param list as created in my code'])

    # print(check_all_user_jobs("shao@bgu.ac.il"))

    # print(get_start_and_end_time("shao@dssd"))

    jobid = run_job_on_gpu('shao@bgu.ac.il', 'SlurmFunctions/./main.py', ['1000000000'])
    print("job ID is: " + str(jobid))
    time.sleep(2)
    cancel_job(jobid)
    print("canceled jobs: " + str(get_user_canceled_jobs("shao@bgu.ac.il")))


# import sched, time
# s = sched.scheduler(time.time, time.sleep)
# def do_something(sc):
#     print("Doing stuff...")
#     # do your stuff
#     s.enter(60, 1, do_something, (sc,))
#
# s.enter(60, 1, do_something, (s,))
# s.run()
