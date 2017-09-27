from typing import List, Dict


class TaskRunner:
    def __init__(self, tasks: List):
        self.tasks = tasks

    def run(self):
        self.__run(enumerate(self.tasks), [])

    def __run(self, tasks, previous_results):
        task = next(tasks)[1]

        if previous_results:
            results = task.run(*previous_results)
        else:
            results = task.run()

        for result in results:
            previous_results.append(result)
            self.__run(tasks, previous_results)
