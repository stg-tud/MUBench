from typing import List
from unittest.mock import MagicMock

from nose.tools import assert_in, assert_raises, assert_equals

from tasks.task_runner import TaskRunner, TaskParameterUnavailableWarning, TaskParameterDuplicateTypeWarning, \
    TaskRequestsDuplicateTypeWarning


class TestTaskRunner:
    def test_runs_first_task(self):
        task = VoidTask()
        uut = TaskRunner([task])

        uut.run()

        task.assert_called_once_with()

    def test_runs_second_task_with_result_of_first_task(self):
        first_task = VoidTask([":some string:"])
        second_task = StringConsumingTask()
        uut = TaskRunner([first_task, second_task])

        uut.run()

        second_task.assert_called_once_with(":some string:")

    def test_runs_second_task_with_each_result_of_first_task(self):
        first_task = VoidTask([":some string:", ":other string:"])
        second_task = StringConsumingTask()
        uut = TaskRunner([first_task, second_task])

        uut.run()

        second_task.assert_has_calls([(":some string:",), (":other string:",)])

    def test_runs_subsequent_task_with_all_results_of_previous_tasks(self):
        first_task = VoidTask([":some string:"])
        second_task = StringConsumingTask([42])
        third_task = StringAndIntConsumingTask()
        uut = TaskRunner([first_task, second_task, third_task])

        uut.run()

        third_task.assert_called_once_with(":some string:", 42)

    def test_runs_subsequent_task_with_required_results_of_previous_tasks(self):
        first_task = VoidTask([":some string:"])
        second_task = VoidTask()
        uut = TaskRunner([first_task, second_task])

        uut.run()

        second_task.assert_called_once_with()

    def test_runs_subsequent_task_with_results_of_previous_tasks_in_any_order(self):
        first_task = VoidTask([":some string:"])
        second_task = StringConsumingTask([42])
        third_task = IntAndStringConsumingTask()
        uut = TaskRunner([first_task, second_task, third_task])

        uut.run()

        third_task.assert_called_once_with(42, ":some string:")

    def test_runs_subsequent_task_with_generic_result_of_previous_task(self):
        first_task = VoidTask([[1,2]])
        second_task = ListConsumingTask()
        uut = TaskRunner([first_task, second_task])

        uut.run()

        second_task.assert_called_once_with([1,2])

    def test_reports_if_a_task_requires_an_unavailable_parameter(self):
        first_task = VoidTask([42])
        second_task = StringConsumingTask()
        uut = TaskRunner([first_task, second_task])

        with assert_raises(TaskParameterUnavailableWarning) as context:
            uut.run()

        actual_message = str(context.exception)
        assert_equals("Missing parameter s for task StringConsumingTask", actual_message)

    def test_reports_if_a_task_returns_the_same_type_as_a_previous_task(self):
        first_task = VoidTask(['-some-string-'])
        second_task = StringConsumingTask(['-some-other-string-'])
        uut = TaskRunner([first_task, second_task])

        with assert_raises(TaskParameterDuplicateTypeWarning) as context:
            uut.run()

        actual_message = str(context.exception)
        assert_equals("Parameter type str provided by task StringConsumingTask already exists", actual_message)

    def test_reports_if_a_task_requests_the_same_type_multiple_times(self):
        first_task = VoidTask([42])
        second_task = DuplicateIntRequestingTask()
        uut = TaskRunner([first_task, second_task])

        with assert_raises(TaskRequestsDuplicateTypeWarning) as context:
            uut.run()

        actual_message = str(context.exception)
        assert_equals("Task DuplicateIntRequestingTask requests multiple parameters of type int", actual_message)

    def test_reports_when_a_task_fails(self):
        task = FailingTask("-error-")
        uut = TaskRunner([task])
        uut.logger = MagicMock()

        uut.run()

        uut.logger.warning.assert_called_once_with("Task FailingTask failed with exception -error-")

    def test_continues_with_next_input_if_task_fails(self):
        first_task = VoidTask(results=["-some string-", "-some other string-"])
        second_task = FailingStringConsumingTask("-error-")
        uut = TaskRunner([first_task, second_task])
        uut.logger = MagicMock()

        uut.run()

        second_task.assert_called_once_with("-some other string-")


class MockTask:
    def __init__(self, results: List = None):
        self.results = results or []
        self.calls = []

    def assert_called_once_with(self, *args):
        self.assert_has_calls([args])

    def assert_has_calls(self, calls):
        for call in calls:
            assert_in(call, self.calls)


class VoidTask(MockTask):
    def run(self):
        self.calls.append(())
        return self.results


class StringConsumingTask(MockTask):
    def run(self, s: str):
        self.calls.append((s,))
        return self.results


class StringAndIntConsumingTask(MockTask):
    def run(self, s: str, i: int):
        self.calls.append((s, i))
        return self.results


class IntAndStringConsumingTask(MockTask):
    def run(self, i: int, s: str):
        self.calls.append((i, s))
        return self.results


class ListConsumingTask(MockTask):
    def run(self, l: List):
        self.calls.append((l,))
        return self.results


class DuplicateIntRequestingTask(MockTask):
    def run(self, i: int, j: int):
        self.calls.append((i, j))
        return self.results


class FailingTask(MockTask):
    def __init__(self, message: str = "", results = None):
        super().__init__(results)
        self.message = message

    def run(self):
        self.calls.append(())
        raise ValueError(self.message)


class FailingStringConsumingTask(MockTask):
    def __init__(self, message: str = "", results = None):
        super().__init__(results)
        self.message = message

    def run(self, s: str):
        self.calls.append((s,))
        raise ValueError(self.message)
