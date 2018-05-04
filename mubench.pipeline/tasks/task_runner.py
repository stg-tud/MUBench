import collections
import logging
from inspect import signature, Parameter

from typing import List, Tuple, Any


class Continue:
    pass


class TaskRunner:
    def __init__(self, tasks: List):
        self.tasks = tasks
        self.logger = logging.getLogger("task_runner")
        self.__accumulated_result = None

    def run(self, *initial_parameters: Tuple[Any]):
        if not self.tasks:
            return

        self.__accumulated_result = None
        self.__run(0, list(initial_parameters))
        for task in self.tasks:
            if callable(getattr(task, 'end', None)):
                task.end()
        return self.__accumulated_result

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

        is_leaf_task = current_task_index == len(self.tasks) - 1
        is_accumulable_result = hasattr(results, '__add__')
        if is_leaf_task and is_accumulable_result:
            if self.__accumulated_result is None:
                self.__accumulated_result = results
            else:
                self.__accumulated_result += results

        if results is None:
            results = [Continue()]

        results = TaskRunner.__as_iterable(results)

        for result in results:
            result_type_already_exists = type(result) in [type(previous_result) for previous_result in previous_results]
            if result_type_already_exists:
                raise TaskParameterDuplicateTypeWarning(task, type(result))

            if current_task_index + 1 < len(self.tasks):
                if isinstance(result, Continue):
                    next_results = previous_results
                else:
                    next_results = previous_results + [result]

                self.__run(current_task_index + 1, next_results)

    @staticmethod
    def __get_parameter_values(task, previous_results):
        parameter_values = []
        for parameter in TaskRunner.__get_parameters(task):
            if parameter.kind == Parameter.VAR_POSITIONAL:
                return previous_results

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
