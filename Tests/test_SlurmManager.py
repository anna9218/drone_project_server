import subprocess
import time
import unittest

from SlurmCommunication import SlurmManager


def run_on_gpu_and_return_output(cmd):
    with open("unitTestOutput.txt", "w+") as fout:
        out = SlurmManager.exe_cmd_on_gpu_server(cmd, fout)
        fout.seek(0)
        output = fout.read()
        subprocess.call(["rm", "unitTestOutput.txt"])
        return output


class TestSlurmMethods(unittest.TestCase):

    def test_exe_cmd_on_gpu_server(self):
        with open("unitTestOutput.txt", "w+") as fout:
            cmd = "ls"
            out = SlurmManager.exe_cmd_on_gpu_server(cmd, fout)
            fout.seek(0)
            output = fout.read()
            self.assertFalse("testDir" in output)
            cmd = "mkdir testDir; ls"
            out = SlurmManager.exe_cmd_on_gpu_server(cmd, fout)
            fout.seek(0)
            output = fout.read()
            self.assertTrue("testDir" in output)
            cmd = "rm -r testDir"
            out = SlurmManager.exe_cmd_on_gpu_server(cmd, fout)
            subprocess.call(["rm", "unitTestOutput.txt"])

    def test_is_sbatch_created_and_filled_correctly(self):
        shao1_name = SlurmManager.create_sbatch_file("shao@post.bgu.ac.il", 'testSlurm/./tst.py', ['127'])
        edenta1_name = SlurmManager.create_sbatch_file("edenta@post.bgu.ac.il", 'testSlurm/./tst.py', ['9963'])
        output = run_on_gpu_and_return_output("ls")
        self.assertTrue(shao1_name in output)
        self.assertTrue(edenta1_name in output)
        expected_output = "#!/bin/bash \n\n" \
                          "#SBATCH --partition main \n" \
                          "#SBATCH --time 0-10:00:00 \n" \
                          "#SBATCH --job-name shao1_job \n" \
                          "#SBATCH --output job-%J.out \n" \
                          "#SBATCH --mail-user=shao@post.bgu.ac.il \n" \
                          "#SBATCH --mail-type=ALL \n" \
                          "#SBATCH --gres=gpu:1 \n" \
                          "#SBATCH --mem=32G \n" \
                          "#SBATCH --cpus-per-task=6 \n" \
                          "### Print some data to output file ### \n" \
                          "echo `date` \n" \
                          "echo -e \"\\nSLURM_JOBID:\\t\\t\" $SLURM_JOBID \n" \
                          "echo -e \"SLURM_JOB_NODELIST:\\t\" $SLURM_JOB_NODELIST \"\\n\\n\" \n\n" \
                          "### Start your code below #### \n" \
                          "module load anaconda \n" \
                          "source activate py36 \n" \
                          "python testSlurm/./tst.py 127 \n\n"
        output = run_on_gpu_and_return_output("cat " + shao1_name)
        self.assertEqual(expected_output, output)

    def test_run_job_and_check_all_user_jobs(self):

        # test run_job_on_gpu:

        shao1_job_id = SlurmManager.run_job_on_gpu("shao@post.bgu.ac.il", 'testSlurm/./tst.py', ['127'])
        edenta1_job_id = SlurmManager.run_job_on_gpu("edenta@post.bgu.ac.il", 'testSlurm/./tst.py', ['9963'])

        name_of_file1 = "job-" + str(shao1_job_id) + ".out"
        name_of_file2 = "job-" + str(edenta1_job_id) + ".out"
        time.sleep(5)

        output = run_on_gpu_and_return_output("ls")

        self.assertTrue("shao1_sbatchFile.txt" in output)
        self.assertTrue("shao1_out.txt" in output)
        self.assertTrue("shao1_err.txt" in output)
        self.assertTrue(name_of_file1 in output)

        self.assertTrue("edenta1_sbatchFile.txt" in output)
        self.assertTrue("edenta1_out.txt" in output)
        self.assertTrue("edenta1_err.txt" in output)
        self.assertTrue(name_of_file2 in output)

        self.assertTrue("slurmtest1234.txt" in output)

        # test get_all_user_jobs:

        shais_job_is_found = False
        edens_job_is_found = False
        all_jobs = SlurmManager.get_all_user_jobs()
        for job in all_jobs:
            if job["job_id"] == shao1_job_id:
                shais_job_is_found = True
            if job["job_id"] == edenta1_job_id:
                edens_job_is_found = True
        self.assertTrue(shais_job_is_found)
        self.assertTrue(edens_job_is_found)

        subprocess.call(["rm", "all_jobs.txt"])
        subprocess.call(["rm", "runJob.txt"])

    def test_cancel_job(self):
        job_id = SlurmManager.run_job_on_gpu("annamiro@post.bgu.ac.il", 'testSlurm/./tst.py', ['10000000'])
        all_jobs = SlurmManager.get_all_user_jobs()
        for job in all_jobs:
            if job["job_id"] == job_id:
                self.assertFalse(job["state"] == "CANCELLED" or job["state"] == "CANCELLED+")
        SlurmManager.cancel_job(job_id)
        for job in all_jobs:
            if job["job_id"] == job_id:
                self.assertTrue(job["state"] == "CANCELLED" or job["state"] == "CANCELLED+")

    def test_move_file_to_gpu(self):
        file_content = "Move this file to GPU!"
        file_name = "fileToMove.txt"
        with open(file_name, "w+") as f:
            out = subprocess.call(["echo", file_content], stdout=f)
        remote_ls = run_on_gpu_and_return_output("ls")
        self.assertFalse(file_name in remote_ls)
        SlurmManager.move_file_to_gpu(file_name, file_name)
        remote_ls = run_on_gpu_and_return_output("ls")
        self.assertTrue(file_name in remote_ls)
        check_if_body_is_same = run_on_gpu_and_return_output("cat " + file_name)
        self.assertEqual(check_if_body_is_same, file_content + "\n\n")
        subprocess.call(["rm", file_name])
        run_on_gpu_and_return_output("rm fileToMove.txt")

    def test_get_job_report(self):
        expected_content = "This is a dummy report.\n"
        actual_content = SlurmManager.get_job_report("annamiro@post.bgu.ac.il", "dummy")
        self.assertEqual(expected_content, actual_content)
        with open("ls.txt", "w+") as fout:
            subprocess.call(["ls"], stdout=fout)
            fout.seek(0)
            local_ls = fout.read()
            self.assertTrue("reportToReturn.txt" in local_ls)
            subprocess.call(["rm", "ls.txt"])
            subprocess.call(["rm", "reportToReturn.txt"])


if __name__ == '__main__':
    unittest.main()

