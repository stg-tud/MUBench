from typing import List

from nose.tools import assert_raises, assert_equals

from tasks.configurations.configurations import TaskConfiguration, get_task_configuration


class ConfigDummy:
    def __init__(self, mode: str):
        self.task = mode


class TestTaskConfigurations:
    def test_get_configuration(self):
        configuration = get_task_configuration(ConfigDummy("-test-"))
        assert_equals(configuration, TaskConfigurationTestImpl.TASKS)

    def test_duplicate_raises_value_error(self):
        assert_raises(ValueError, get_task_configuration, ConfigDummy("-duplicate-"))

    def test_no_available_configuration_raises_value_error(self):
        assert_raises(ValueError, get_task_configuration, ConfigDummy("-unavailable-"))


class TaskConfigurationTestImpl(TaskConfiguration):
    TASKS = ["-a-", "-b-", "-c-"]

    @staticmethod
    def mode() -> str:
        return "-test-"

    def tasks(self, config) -> List:
        return TaskConfigurationTestImpl.TASKS


class DuplicateTaskConfiguration(TaskConfiguration):
    def tasks(self, config) -> List:
        return []

    @staticmethod
    def mode() -> str:
        return "-duplicate-"


class DuplicateTaskConfiguration2(TaskConfiguration):
    def tasks(self, config) -> List:
        return []

    @staticmethod
    def mode() -> str:
        return "-duplicate-"
