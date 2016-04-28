import sys
from datetime import datetime

from checkout import do_all_checkouts
from detector_runner import run_detector_on_all_data
from result_evaluation import evaluate_results
from utils.prerequisites_checker import check_prerequisites


def check():
    print("Checking prerequisites... ", end="")  # remove newline to append the later okay directly
    prerequisites_okay, error_message = check_prerequisites()
    if not prerequisites_okay:
        print('')  # add the before omitted newline
        sys.exit(error_message)
    print("okay!")


def checkout():
    do_all_checkouts()


def mine():
    pass  # TODO implement a miner_runner


def evaluate():
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
        evaluate_results()
        end_time = datetime.now()
        print("Total evaluation time: {}".format(str(end_time - start_time)))

        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("++++++++++++++++++++++++ FINISHED +++++++++++++++++++++++++")
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


check()
checkout()
evaluate()
