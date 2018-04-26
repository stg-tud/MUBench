from sys import getsizeof, stderr
from itertools import chain
from collections import deque


__default_handlers = {tuple: iter,
                      list: iter,
                      deque: iter,
                      dict: lambda d: chain.from_iterable(d.items()),
                      set: iter,
                      frozenset: iter,
                      }


# source: https://code.activestate.com/recipes/577504/
def total_size(o, verbose=False, additional_handlers=None):
    """ Returns the approximate memory footprint an object and all of its contents.

    Automatically finds the contents of the following builtin containers and
    their subclasses:  tuple, list, deque, dict, set and frozenset.
    To search other containers, add handlers to iterate over their contents:

        handlers = {SomeContainerClass: iter,
                    OtherContainerClass: OtherContainerClass.get_elements}

    """
    seen = set()  # track which object id's have already been seen
    default_size = getsizeof(0)  # estimate sizeof object without __sizeof__
    handlers = dict(__default_handlers)
    if additional_handlers:
        handlers.update(additional_handlers)

    def sizeof(obj):
        if id(obj) in seen:  # do not double count the same object
            return 0
        seen.add(id(obj))
        s = getsizeof(obj, default_size)

        if verbose:
            print(s, type(obj), repr(obj), file=stderr)

        for type_, handler in handlers.items():
            if isinstance(obj, type_):
                s += sum(map(sizeof, handler(obj)))
                break
        return s

    return sizeof(o)
