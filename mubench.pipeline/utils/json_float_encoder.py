# source: https://gist.github.com/pauloalem/6244976
import json


class JSONFloatEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(JSONFloatEncoder, self).__init__(*args, **kwargs)

    def iterencode(self, o, _one_shot=False):
        """Encode the given object and yield each string
        representation as available.

        For example::

        for chunk in JSONEncoder().iterencode(bigobject):
        mysocket.write(chunk)
        """
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = json.encoder.encode_basestring_ascii
        else:
            _encoder = json.encoder.encode_basestring

        def floatstr(o, allow_nan=self.allow_nan):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            if o != o: # NaN != NaN
                text = 'NaN'
            elif o == float('inf'):
                text = 'Infinity'
            elif o == float('-inf'):
                text = '-Infinity'
            else:
                return repr(o)

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            return text

        _iterencode = json.encoder._make_iterencode(markers, self.default,
                                                    _encoder, self.indent,
                                                    floatstr, self.key_separator,
                                                    self.item_separator, self.sort_keys,
                                                    self.skipkeys, _one_shot)
        return _iterencode(o, 0)
