from sys import getsizeof

from nose.tools import assert_equals

from utils.size import total_size


class TestSize:
    class ObjectWithFixedSize:
        def __sizeof__(self):
            return 42

    def test_size_of_object(self):
        assert_equals(total_size(TestSize.ObjectWithFixedSize()), 42 + getsizeof(0))

    def test_additional_collection_handler(self):
        class C:
            pass

        def get_items(_):
            get_items.called = True
            return [TestSize.ObjectWithFixedSize()]

        get_items.called = False

        total_size(C(), additional_handlers={C: get_items})

        assert_equals(get_items.called, True)
