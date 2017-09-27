from inspect import signature, Parameter

from typing import List


class TaskRunner:
    def __init__(self, tasks: List):
        self.tasks = tasks

    def run(self):
        self.__run(0, [])

    def __run(self, current_task_index: int, previous_results: List):
        task = self.tasks[current_task_index]
        parameter_values = self.__get_parameter_values(task, previous_results)
        results = task.run(*parameter_values)
        for result in results:
            next_results = previous_results + [result]
            self.__run(current_task_index + 1, next_results)

    @staticmethod
    def __get_parameter_values(task, previous_results):
        parameter_values = []
        for parameter in TaskRunner.__get_parameters(task):
            parameter_value = TaskRunner.__find_value(parameter, previous_results)
            if parameter_value:
                parameter_values.append(parameter_value)
            else:
                raise TaskParameterUnavailableWarning(task, parameter)
        return parameter_values

    @staticmethod
    def __get_parameters(task):
        return signature(task.run).parameters.values()

    @staticmethod
    def __find_value(parameter: Parameter, previous_results):
        for value in previous_results:
            if isinstance(value, parameter.annotation):
                return value
        return None


class TaskParameterUnavailableWarning(UserWarning):
    def __init__(self, task, parameter: Parameter):
        super().__init__("Missing parameter {} for task {}".format(parameter.name, type(task).__name__))
        self.task = task
        self.parameter = parameter
