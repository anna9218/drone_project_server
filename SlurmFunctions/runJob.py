import os
import subprocess
import sys


def run_job(sbatch_file_name):
    # output save in out.txt
    job_name = sbatch_file_name.split('_sbatchFile.txt')
    with open(job_name[0]+"_out.txt", 'w+') as fout:
        # errors saved in err.txt
        with open(job_name[0]+"_err.txt", 'w+') as ferr:
            out = subprocess.call(["sbatch", sbatch_file_name], stdout=fout, stderr=ferr)
            os.chmod(job_name[0]+"_out.txt", 0o777)
            # reset file to read from it
            fout.seek(0)
            # save output (if any) in variable
            output = fout.read()
            print(output)


if __name__ == "__main__":
    args = sys.argv
    # args[0] == fileName
    # user_email = args[1]
    sbatch_file_name = args[1]
    run_job(sbatch_file_name)
    # run_job("shao@post.bgu.ac.il", ".././myTestBatch.txt")
