import unittest

from os import path
import time

from SlurmCommunication import SlurmManager


class TestSlurmMethods(unittest.TestCase):

    def test_create_sbatch(self):
        batch_1_name = SlurmManager.create_sbatch_file("shao@post.bgu.ac.il", '../testSlurm/./SlurmManager.py', ['127'])
        batch_2_name = SlurmManager.create_sbatch_file("shao@post.bgu.ac.il", '../testSlurm/./SlurmManager.py', ['50'])
        batch_3_name = SlurmManager.create_sbatch_file("edenta@post.bgu.ac.il", '../testSlurm/./SlurmManager.py', ['9963'])
        self.assertTrue(path.exists("shao1_sbatchFile.txt"))
        self.assertTrue(path.exists("shao2_sbatchFile.txt"))
        self.assertTrue(path.exists("edenta3_sbatchFile.txt"))

    def test_is_sbatch_filled_correctly(self):
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
                          "source activate projenv \n" \
                          "python ../testSlurm/./SlurmManager.py 127 \n"
        with open("shao1_sbatchFile.txt", "r") as batch:
            output = batch.read()
            self.assertEqual(expected_output, output)

    def test_run_job_and_check_all_user_jobs(self):
        shao1_job_id = SlurmManager.run_job("shao", "shao1_sbatchFile.txt")
        shao2_job_id = SlurmManager.run_job("shao", "shao2_sbatchFile.txt")
        edenta3_job_id = SlurmManager.run_job("edenta", "edenta3_sbatchFile.txt")
        name_of_file1 = "job-" + shao1_job_id + ".out"
        name_of_file2 = "job-" + shao2_job_id + ".out"
        name_of_file3 = "job-" + edenta3_job_id + ".out"
        time.sleep(5)
        self.assertTrue(path.exists("shao1_sbatchFile.txt"))
        self.assertTrue(path.exists("shao1_out.txt"))
        self.assertTrue(path.exists("shao1_err.txt"))
        self.assertTrue(path.exists(name_of_file1))
        self.assertTrue(path.exists("shao2_sbatchFile.txt"))
        self.assertTrue(path.exists("shao2_out.txt"))
        self.assertTrue(path.exists("shao2_err.txt"))
        self.assertTrue(path.exists(name_of_file2))
        self.assertTrue(path.exists("edenta3_sbatchFile.txt"))
        self.assertTrue(path.exists("edenta3_out.txt"))
        self.assertTrue(path.exists("edenta3_err.txt"))
        self.assertTrue(path.exists(name_of_file3))

        self.assertTrue(path.exists("slurmtest1234.txt"))

        for name in ['shao', 'edenta', 'anna']:
            is_found1 = False
            is_found2 = False
            is_found3 = False
            user_jobs_list = SlurmManager.check_all_user_jobs(name)
            actual_split0 = user_jobs_list[0].split(" ")
            actual_split0 = [x for x in actual_split0 if x]
            actual_split1 = user_jobs_list[1].split(" ")
            actual_split1 = [x for x in actual_split1 if x]
            self.assertEquals(actual_split0, ["JobID", "JobName", "Partition", "Account", "AllocCPUS", "State", "ExitCode"])
            self.assertEquals(actual_split1, ['------------', '----------', '----------', '----------', '----------', '----------', '--------'])
            if name == 'shao':
                for word in user_jobs_list:
                    if shao1_job_id in word:
                        is_found1 = True
                for word in user_jobs_list:
                    if shao2_job_id in word:
                        is_found2 = True
                for word in user_jobs_list:
                    if edenta3_job_id in word:
                        is_found3 = True
                self.assertTrue(is_found1)
                self.assertTrue(is_found2)
                self.assertFalse(is_found3)
            if name == 'edenta':
                for word in user_jobs_list:
                    if shao1_job_id in word:
                        is_found1 = True
                for word in user_jobs_list:
                    if shao2_job_id in word:
                        is_found2 = True
                for word in user_jobs_list:
                    if edenta3_job_id in word:
                        is_found3 = True
                self.assertFalse(is_found1)
                self.assertFalse(is_found2)
                self.assertTrue(is_found3)
            if name == 'anna':
                for word in user_jobs_list:
                    if shao1_job_id in word:
                        is_found1 = True
                for word in user_jobs_list:
                    if shao2_job_id in word:
                        is_found2 = True
                for word in user_jobs_list:
                    if edenta3_job_id in word:
                        is_found3 = True
                self.assertFalse(is_found1)
                self.assertFalse(is_found2)
                self.assertFalse(is_found3)

    # def test_check_all_user_jobs(self):
    #     for name in ['shao', 'edenta', 'anna']:
    #         user_jobs_list = check_all_user_jobs(name)
    #         actual_split0 = user_jobs_list[0].split(" ")
    #         actual_split0 = [x for x in actual_split0 if x]
    #         actual_split1 = user_jobs_list[1].split(" ")
    #         actual_split1 = [x for x in actual_split1 if x]
    #         self.assertEquals(actual_split0, ["JobID", "JobName", "Partition", "Account", "AllocCPUS", "State", "ExitCode"])
    #         self.assertEquals(actual_split1, ['------------', '----------', '----------', '----------', '----------', '----------', '--------'])
    #         if name == 'shao':
    #             print(user_jobs_list)
    #             self.assertTrue(self.test_job_id1 in user_jobs_list)
    #             self.assertTrue(self.test_job_id2 in user_jobs_list)
    #             self.assertFalse(self.test_job_id3 in user_jobs_list)
    #         if name == 'edenta':
    #             print(user_jobs_list)
    #             self.assertFalse(self.test_job_id1 in user_jobs_list)
    #             self.assertFalse(self.test_job_id2 in user_jobs_list)
    #             # self.assertTrue(self.test_job_id3 in user_jobs_list)
    #         if name == 'anna':
    #             print(user_jobs_list)
    #             # self.assertFalse(self.test_job_id1 in user_jobs_list)
    #             # self.assertFalse(self.test_job_id2 in user_jobs_list)
    #             # self.assertFalse(self.test_job_id3 in user_jobs_list)


if __name__ == '__main__':
    unittest.main()
    # print("\nusers and jobs:\n")
    # print(users_and_jobs)
