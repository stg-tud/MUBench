import collections
import logging
from inspect import signature, Parameter

from typing import List


class Continue:
    pass


class TaskRunner:
    def __init__(self, tasks: List):
        self.tasks = tasks
        self.logger = logging.getLogger("task_runner")

    def run(self):
        self.__run(0, [])
        for task in self.tasks:
            if callable(getattr(task, 'end', None)):
                task.end()

    def __run(self, current_task_index: int, previous_results: List):
        task = self.tasks[current_task_index]
        parameter_values = self.__get_parameter_values(task, previous_results)

        task_name = type(task).__name__
        self.logger.debug("Running task {}".format(task_name))
        self.logger.debug("Parameters: {}".format([str(v) for v in parameter_values]))

        try:
            results = task.run(*parameter_values)
        except Exception as exception:
            logger = logging.getLogger("task_runner.{}".format(task_name))
            logger.warning("%s", exception)
            logger.debug("Full exception:", exc_info=True)
            return

        if results is None:
            results = [Continue()]

        if len(results) == 0:
            logger = logging.getLogger("task_runner.{}".format(task_name))
            logger.warning("Task {} returned no results; skipping succeeding tasks.".format(task_name))

        for result in TaskRunner.__as_iterable(results):
            result_type_already_exists = type(result) in [type(previous_result) for previous_result in previous_results]
            if result_type_already_exists:
                raise TaskParameterDuplicateTypeWarning(task, type(result))

            if current_task_index + 1 < len(self.tasks):
                next_task = type(self.tasks[current_task_index + 1]).__name__

                if isinstance(result, Continue):
                    next_results = previous_results
                else:
                    next_results = previous_results + [result]

                self.logger.info("Running %s on %s", next_task, result)
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
    def __as_iterable(previous_results):
        if isinstance(previous_results, collections.Iterable) and not isinstance(previous_results, str):
            return previous_results
        else:
            return [previous_results]

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
