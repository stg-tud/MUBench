from nose.tools import assert_equals

from benchmark.utils.data_util import normalize_data_misuse_path, normalize_result_misuse_path


def test_normalize_git_path_from_data():
    non_normalized_path = r'src/main/java/com/alibaba/druid/filter/config/ConfigTools.java'
    expected_normalized_path = r'com/alibaba/druid/filter/config/ConfigTools.java'
    actual_normalized_path = normalize_data_misuse_path(non_normalized_path, r"src/main/java/")
    assert_equals(expected_normalized_path, actual_normalized_path)


def test_normalize_svn_path_from_data():
    non_normalized_path = r'incubator/jackrabbit/trunk/src/java/org/apache/jackrabbit/core/state/obj/ObjectPersistenceManager.java'
    expected_normalized_path = r'org/apache/jackrabbit/core/state/obj/ObjectPersistenceManager.java'
    actual_normalized_path = normalize_data_misuse_path(non_normalized_path, r"src/java/")
    assert_equals(expected_normalized_path, actual_normalized_path)


def test_normalize_synthetic_path_from_data():
    non_normalized_path = r'synthetic-androidactivity-1.java'
    expected_normalized_path = r'synthetic-androidactivity-1.java'
    actual_normalized_path = normalize_data_misuse_path(non_normalized_path, None)
    assert_equals(expected_normalized_path, actual_normalized_path)


def test_normalize_git_path_from_result():
    non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\alibaba-druid\src\main\java\com\alibaba\druid\filter\config\ConfigTools.java'
    expected_normalized_path = r'com/alibaba/druid/filter/config/ConfigTools.java'
    actual_normalized_path = normalize_result_misuse_path(non_normalized_path,
                                                          r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark', r"src/main/java/")
    assert_equals(expected_normalized_path, actual_normalized_path)


def test_normalize_svn_path_from_result():
    non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\jackrabbit\trunk\src\java\org\apache\jackrabbit\core\state\obj\ObjectPersistenceManager.java'
    expected_normalized_path = r'org/apache/jackrabbit/core/state/obj/ObjectPersistenceManager.java'
    actual_normalized_path = normalize_result_misuse_path(non_normalized_path,
                                                          r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark', r"src/java/")
    assert_equals(expected_normalized_path, actual_normalized_path)


def test_normalize_synthetic_path_from_result():
    non_normalized_path = r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark\synthetic-androidactivity-1\synthetic-androidactivity-1.java'
    expected_normalized_path = r'synthetic-androidactivity-1.java'
    actual_normalized_path = normalize_result_misuse_path(non_normalized_path,
                                                          r'C:\Users\m8is\AppData\Local\Temp\MUBenchmark', None)
    assert_equals(expected_normalized_path, actual_normalized_path)
