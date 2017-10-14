import logging
from inspect import signature, Parameter

from typing import List


class TaskRunner:
    def __init__(self, tasks: List):
        self.tasks = tasks
        self.logger = logging.getLogger("taskrunner")

    def run(self):
        self.__run(0, [])
        for task in self.tasks:
            if callable(getattr(task, 'end', None)):
                task.end()

    def __run(self, current_task_index: int, previous_results: List):
        task = self.tasks[current_task_index]
        parameter_values = self.__get_parameter_values(task, previous_results)

        task_name = type(task).__name__
        self.logger.info("Running task {}".format(task_name))
        self.logger.debug("Parameters: {}".format([str(v) for v in parameter_values]))

        try:
            results = task.run(*parameter_values)
        except Exception as exception:
            self.logger.warning("Task {} failed with exception {}".format(task_name, exception))
            results = []

        for result in results:
            result_type_already_exists = type(result) in [type(previous_result) for previous_result in previous_results]
            if result_type_already_exists:
                raise TaskParameterDuplicateTypeWarning(task, type(result))
            next_results = previous_results + [result]
            self.__run(current_task_index + 1, next_results)

    @staticmethod
    def __get_parameter_values(task, previous_results):
        parameter_values = []
        for parameter in TaskRunner.__get_parameters(task):
            parameter_value = TaskRunner.__find_value(parameter, previous_results)
            if parameter_value:
                if type(parameter_value) in [type(existing_value) for existing_value in parameter_values]:
                    raise TaskRequestsDuplicateTypeWarning(task, type(parameter_value))
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


class TaskParameterDuplicateTypeWarning(UserWarning):
    def __init__(self, task, type_: type):
        super().__init__(
            "Parameter type {} provided by task {} already exists".format(type_.__name__, type(task).__name__))


class TaskRequestsDuplicateTypeWarning(UserWarning):
    def __init__(self, task, type_: type):
        super().__init__("Task {} requests multiple parameters of type {}".format(type(task).__name__, type_.__name__))
