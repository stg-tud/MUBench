from typing import List, Dict


class TaskRunner:
    def __init__(self, tasks: List):
        self.tasks = tasks

    def run(self):
        self.__run(0, [])

    def __run(self, current_task_index: int, previous_results: List):
        task = self.tasks[current_task_index]

        if previous_results:
            results = task.run(*previous_results)
        else:
            results = task.run()

        for result in results:
            next_results = previous_results + [result]
            self.__run(current_task_index + 1, next_results)
