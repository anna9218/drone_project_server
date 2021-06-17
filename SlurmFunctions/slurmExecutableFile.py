"""
    This file should be located on the GPU server in SlurmFunctions directory!
"""
import os
import sys
import traceback
from functools import reduce
import jinja2
from jsonpickle import json

sys.path.append(os.getcwd().split('\SlurmFunctions')[0])
from SlurmFunctions.SplitData import SplitData

FILES_DIR = "SlurmFunctions.models."


def create_and_run_model(user_email: str, job_name_by_user: str, model_type: str,
                         model_details: dict, dataset_path: str, output_size: int, num_of_features: int) -> None:
    original_stdout = sys.stdout
    user_name = user_email.split('@')[0]
    # saves the job's report in file on GPU server located in SlurmFunctions/reports
    with open('./SlurmFunctions/reports/' + user_name + '_' + job_name_by_user + '_report.txt', 'w') as report_file:
        try:
            sys.stdout = report_file

            #  ----------------------------  printing to report file  ----------------------------
            x_train, y_train, x_test, y_test = SplitData(num_of_features).split_to_train_test_from_csv(dataset_path)
            os.remove(dataset_path)

            print('Split data successfully:')
            print('     x_train shape: ' + json.dumps(x_train.shape))
            print('     y_train shape: ' + json.dumps(y_train.shape))
            print('     x_test shape:  ' + json.dumps(x_test.shape))
            print('     y_test shape:  ' + json.dumps(y_test.shape))

            # creates Class Object of type model_type, A class that inherits from  Model class
            new_model = getattr(jinja2.utils.import_string(FILES_DIR + model_type), model_type)(model_details)
            new_model.set_output_size(output_size)
            new_model.set_train_test_sets(x_train, y_train, x_test, y_test)
            print('Create CNN model successfully.')
            report: dict = new_model.train_and_predict_model()
            print('CNN model results:')
            [print('     ' + key + ': ' + report[key]) for key in report.keys()]
            #  -----------------------------------------------------------------------------------

            sys.stdout = original_stdout
            report_file.close()
        except Exception as e:
            print('\n*********************************************\n')
            print('Exception occurred while running the job on Slurm servers.\n'
                  'Please check the executable file located on Slurm (= GPU server: shao@gpu.bgu.ac.il)\n'
                  'Exception\'s details: ', e)
            print('Exception\'s traceback:')
            # traceback.print_exc()
            print(traceback.format_exc())
            print('\n*********************************************\n')
            report_file.close()
            sys.stdout = original_stdout
    sys.stdout = original_stdout
    print('\nJob ended successfully.\n')


if __name__ == "__main__":
    args = sys.argv
    # args[0] == fileName.
    whatToDo = args[1]
    if whatToDo == "createAndRunModel":
        job_name_by_user = args[2]
        model_type = args[3]
        dataset_path = args[4]
        user_email = args[5]
        output_size = int(args[6])
        num_of_features = int(args[7])
        model_details_str = reduce(lambda acc, curr: acc + curr, args[8:])
        model_details = json.loads(model_details_str)
        create_and_run_model(user_email, job_name_by_user, model_type, model_details, dataset_path, output_size, num_of_features)
