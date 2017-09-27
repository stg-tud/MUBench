from unittest.mock import MagicMock

from tasks.task_runner import TaskRunner


class TestTaskRunner:
    def test_runs_first_task(self):
        task = MagicMock()
        uut = TaskRunner([task])

        uut.run()

        task.run.assert_called_once_with()
