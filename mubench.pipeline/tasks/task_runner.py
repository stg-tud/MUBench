from typing import List


class TaskRunner:
    def __init__(self, tasks: List):
        self.tasks = tasks

    def run(self):
        for task in self.tasks:
            task.run()
