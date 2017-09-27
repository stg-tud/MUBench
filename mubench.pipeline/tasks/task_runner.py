from typing import List, Dict


class TaskRunner:
    def __init__(self, tasks: List):
        self.tasks = tasks

    def run(self):
        self.__run(enumerate(self.tasks))

    def __run(self, tasks, result = None):
        task = next(tasks)[1]

        if result:
            results = task.run(result)
        else:
            results = task.run()

        for result in results:
            self.__run(tasks, result)
