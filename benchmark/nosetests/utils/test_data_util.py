from os.path import join

from benchmark.utils.data_util import normalize_data_misuse_path, normalize_result_misuse_path, \
    extract_project_name_from_file_path


def test_extract_normal_name():
    expected = "some-project"
    actual = extract_project_name_from_file_path(join("C:", "my-path", "{}.42-2.yml".format(expected)))
    assert actual == expected


def test_extract_synthetic_name():
    expected = "synthetic-case"
    actual = extract_project_name_from_file_path((join("C:", "my-path", "{}.yml".format(expected))))
    assert actual == expected


def test_normalize_git_path_from_data():
    non_normalized_path = r'src/main/java/com/alibaba/druid/filter/config/ConfigTools.java'
    expected_normalized_path = r'src\main\java\com\alibaba\druid\filter\config\ConfigTools.java'
    actual_normalized_path = normalize_data_misuse_path(non_normalized_path)
    assert actual_normalized_path == expected_normalized_path


def test_normalize_svn_path_from_data():
    non_normalized_path = r'incubator/jackrabbit/trunk/src/java/org/apache/jackrabbit/core/state/obj/ObjectPersistenceManager.java'
    expected_normalized_path = r'src\java\org\apache\jackrabbit\core\state\obj\ObjectPersistenceManager.java'
    actual_normalized_path = normalize_data_misuse_path(non_normalized_path)
    assert actual_normalized_path == expected_normalized_path


def test_normalize_synthetic_path_from_data():
    non_normalized_path = r'synthetic-androidactivity-1.java'
    expected_normalized_path = r'synthetic-androidactivity-1.java'
    actual_normalized_path = normalize_data_misuse_path(non_normalized_path)
    assert actual_normalized_path == expected_normalized_path


def test_normalize_git_path_from_result():
    non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\alibaba-druid\src\main\java\com\alibaba\druid\filter\config\ConfigTools.java'
    expected_normalized_path = r'src\main\java\com\alibaba\druid\filter\config\ConfigTools.java'
    actual_normalized_path = normalize_result_misuse_path(non_normalized_path,
                                                          r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark')
    assert actual_normalized_path == expected_normalized_path


def test_normalize_svn_path_from_result():
    non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\jackrabbit\trunk\src\java\org\apache\jackrabbit\core\state\obj\ObjectPersistenceManager.java'
    expected_normalized_path = r'src\java\org\apache\jackrabbit\core\state\obj\ObjectPersistenceManager.java'
    actual_normalized_path = normalize_result_misuse_path(non_normalized_path,
                                                          r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark')
    assert actual_normalized_path == expected_normalized_path


def test_normalize_synthetic_path_from_result():
    non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\synthetic-androidactivity-1\synthetic-androidactivity-1.java'
    expected_normalized_path = r'synthetic-androidactivity-1.java'
    actual_normalized_path = normalize_result_misuse_path(non_normalized_path,
                                                          r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark')
    assert actual_normalized_path == expected_normalized_path
