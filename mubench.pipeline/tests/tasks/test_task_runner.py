from unittest.mock import MagicMock, call

from tasks.task_runner import TaskRunner


class TestTaskRunner:
    def test_runs_first_task(self):
        task = MagicMock()
        uut = TaskRunner([task])

        uut.run()

        task.run.assert_called_once_with()

    def test_runs_second_task_with_result_of_first_task(self):
        first_task = MagicMock()
        first_task.run.return_value = [":some string:"]
        second_task = MagicMock()
        uut = TaskRunner([first_task, second_task])

        uut.run()

        second_task.run.assert_called_once_with(":some string:")

    def test_runs_second_task_with_each_result_of_first_task(self):
        first_task = MagicMock()
        first_task.run.return_value = [":some string:", ":other string:"]
        second_task = MagicMock()
        uut = TaskRunner([first_task, second_task])

        uut.run()

        # Would like to ensure order here, but calls contains additional elements 'call().__iter__()` (transitive calls
        # on the result of run()), which we cannot even specify in the test.
        second_task.run.assert_has_calls([call(":some string:"), call(":other string:")], any_order=True)

    def test_runs_subsequent_task_with_results_of_all_previous_tasks(self):
        first_task = MagicMock()
        first_task.run.return_value = [":some string:"]
        second_task = MagicMock()
        second_task.run.return_value = [42]
        third_task = MagicMock()
        uut = TaskRunner([first_task, second_task, third_task])

        uut.run()

        third_task.run.assert_called_once_with(":some string:", 42)
