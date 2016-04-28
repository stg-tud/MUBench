import sys
from datetime import datetime

from detector_runner import run_detector_on_all_data
from result_evaluation import evaluate_results
from utils.prerequisites_checker import check_prerequisites

prerequisites_okay, error_message = check_prerequisites()
if not prerequisites_okay:
    sys.exit(error_message)

try:
    start_time = datetime.now()
    run_detector_on_all_data()

except (KeyboardInterrupt, SystemExit):
    end_time = datetime.now()
    print("================================================")
    print("Analysis cancelled! Total time: {}".format(str(end_time - start_time)))
    print("================================================")
else:
    end_time = datetime.now()
    print("================================================")
    print("Analysis finished! Total time: {}".format(str(end_time - start_time)))
    print("================================================")

finally:
    print("Evaluating results...")
    evaluation_start_time = datetime.now()
    evaluate_results()
    end_time = datetime.now()
    print("Evaluation time: {} ; Complete benchmark time: {}".format(str(end_time - evaluation_start_time),
                                                                     str(end_time - start_time)))

    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("++++++++++++++++++++++++ FINISHED +++++++++++++++++++++++++")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
