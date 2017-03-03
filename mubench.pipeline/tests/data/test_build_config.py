from nose.tools import assert_equals, assert_not_equals

from data.build_config import BuildConfig


class TestBuildConfig:
    def test_to_string(self):
        assert_equals("[src: a, classes: b, commands: ['echo c', 'echo d']]",
                      str(BuildConfig("a", ["echo c", "echo d"], "b")))

    def test_equals(self):
        assert BuildConfig("src", ["command"], "classes") == BuildConfig("src", ["command"], "classes")

    def test_not_equals_src(self):
        assert BuildConfig("src", ["command"], "classes") != BuildConfig("other", ["command"], "classes")

    def test_not_equals_command(self):
        assert BuildConfig("src", ["command"], "classes") != BuildConfig("src", ["other"], "classes")

    def test_not_equals_classes(self):
        assert BuildConfig("src", ["command"], "classes") != BuildConfig("src", ["command"], "other")

    def test_hash_not_equals(self):
        assert_not_equals(hash(BuildConfig("", [], "")), hash(BuildConfig("a", ["b"], "c")))

    def test_hash_equals(self):
        assert_equals(hash(BuildConfig("a", ["b"], "c")), hash(BuildConfig("a", ["b"], "c")))
