from nose.tools import assert_in
from typing import List

from tasks.task_runner import TaskRunner


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

    def test_runs_subsequent_task_with_results_of_all_previous_tasks(self):
        first_task = VoidTask([":some string:"])
        second_task = StringConsumingTask([42])
        third_task = StringAndIntConsumingTask()
        uut = TaskRunner([first_task, second_task, third_task])

        uut.run()

        third_task.assert_called_once_with(":some string:", 42)

    def test_drops_previous_results_if_subsequent_task_does_not_declare_respective_parameter(self):
        first_task = VoidTask([":some string:"])
        second_task = VoidTask()
        uut = TaskRunner([first_task, second_task])

        uut.run()

        second_task.assert_called_once_with()


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
