from datetime import datetime

from benchmark import analyze
from datareader import on_all_data_do
from logger import log_error
from results import evaluate_results

errors = []
try:
    start_time = datetime.now()
    errors = on_all_data_do(analyze)
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
    for error in errors:
        if error is not None:
            log_error(error)

    print("Evaluating results...")
    evaluation_start_time = datetime.now()
    evaluate_results()
    end_time = datetime.now()
    print("Evaluation time: {} ; Complete benchmark time: {}".format(str(end_time - evaluation_start_time),
                                                                     str(end_time - start_time)))
