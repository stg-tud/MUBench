from datetime import datetime

from benchmark import analyze
from datareader import on_all_data_do
from logger import log
from results import evaluate_results

start_time = datetime.now()

results = on_all_data_do(analyze)
for result in results:
    log(result)

end_time = datetime.now()

print("================================================")
print("Analysis finished! Total time: {}".format(str(end_time - start_time)))
print("================================================")

print("Evaluating results...")
evaluation_start_time = datetime.now()
evaluate_results()
end_time = datetime.now()
print("Evaluation time: {} ; Complete benchmark time: {}".format(str(end_time - evaluation_start_time),
                                                                 str(end_time - start_time)))
