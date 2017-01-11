"""Message objects
"""

import re
import logging

import sungrow
import sungrow.config

LOG = logging.getLogger('sungrow.message')


class Message(object):
    """Message objects

    Have key:value parameters, the parameters themselves carrying
    some metadata.  Can be converted to and from bytes.

    These objects have a subset of the dict API; because they have
    predefined keys (in the "names" class attribute), addition of
    arbitrary key:value pairs is not supported.  Order of keys and
    values is preserved by methods like keys(), values(), items().
    """

    names = NotImplemented
    fields = NotImplemented
    length = None
    regexp = NotImplemented
    examples = ()
    _raw_keys = ()
    _discard = {}
    _tenths = ()
    _ints = ()
    _floats = ()
    _mappings = {}
    _bitfields = {}

    def __init__(self, items=()):
        mapping = dict(items)
        keys = set(mapping.keys())
        expected_keys = set(self.names)
        extra = keys - expected_keys
        missing = expected_keys - keys
        if extra:
            raise ValueError('extra keys: {0}'.format(tuple(extra)))
        elif missing:
            raise ValueError('missing keys: {0}'.format(tuple(missing)))
        self._dict = mapping

    def __eq__(self, other):
        """Support for equality operator self == other
        """
        return (isinstance(other, self.__class__) and
                self._dict == other._dict)

    def __ne__(self, other):
        """Support for inequality operator self != other
        """
        return not self.__eq__(other)

    @classmethod
    def from_bytes(cls, raw_message):
        """Create message from native-format bytestring
        """
        ## This base implementation returns an "empty" class, suitable
        ##   for a message with no parameters
        cls._verify_message(raw_message)
        return cls()

    @classmethod
    def many_from_bytes(cls, bytestring):
        """Find all valid messages of this class in bytestring

        Each item in the return sequence is a
        (start_byte, negative_length, message) tuple;
        negative_length is present as a tiebreaker to facilitate
        sorting by earliest-starting and longest messages.

        The matched portions of the bytestring may overlap!  It is up
        to the caller to resolve any such conflicts.
        """
        messages = []
        matches = list(cls.regexp.finditer(bytestring))
        for match in matches:
            substring = match.group(0)
            try:
                message = cls.from_bytes(substring)
            except sungrow.BadBinaryMessage:
                LOG.debug('bad substring {0!r}'.format(substring))
                continue
            ## see docstring for explanation of why -len(substring)
            item = (match.start(), -len(substring), message)
            messages.append(item)
        return messages

    def __repr__(self):
        """Like OrderedDict, give class name and parameters
        """
        return '{0}({1})'.format(self.__class__.__name__,
                                 repr(self._dict))

    def __len__(self):
        return len(self.names)

    def to_bytes(self):
        """Produce native-format bytestring from message
        """
        raise NotImplementedError('deferred to subclasses')

    def __iter__(self):
        """Iterator through ordered sequence of keys
        """
        return iter(self.names)

    def keys(self):
        """Ordered list of keys
        """
        return list(self.names)

    def values(self):
        """Ordered list of values
        """
        return [self[key] for key in self.names]

    def items(self):
        """Ordered list of (key, value) pairs
        """
        return [(key, self[key]) for key in self.names]

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        if key not in self.names:
            raise ValueError('no field {0!r} in {1}'.format(\
                    key, self.__class__.__name__))
        self._dict[key] = value

    def format_data(self, read_time, delimiter=','):
        """Create a delimited text version of message, ordered per names

        First entry in the row will be the formatted read_time.  This
        means that messages with no parameters will return only the
        formatted read time.
        """
        values = ([read_time.strftime(sungrow.config.DATE_FORMAT)] +
                  [str(value) for value in self.values()])
        ## quoting for fields with a comma
        for i, value in enumerate(values):
            if ',' in value:
                values[i] = '"{0}"'.format(value)
        return delimiter.join(values)

    def format_header(self, delimiter=','):
        """Create a delimited text header with ordered names

        First entry in the row is the read time.
        """
        return delimiter.join(['datetime'] + list(self.names))

    @classmethod
    def _verify_checksum(cls, raw_message):
        """Verify raw_message's checksum against its digest

        Throws ChecksumError if they do not match.
        """
        digest = cls._get_digest(raw_message)
        checksum = cls._get_checksum(raw_message)
        if digest != checksum:
            raise sungrow.ChecksumError('{0} != {1}'.format(digest, checksum))

    @classmethod
    def _verify_message(cls, raw_message):
        """Verify length and checksum of raw message

        Throws BadBinaryMessage if raw_message does not have correct length
        or signature, ChecksumError if checksum is bad
        """
        if cls.length is not None:
            if len(raw_message) != cls.length:
                error_msg = 'length {0:d} != {1:d}'.format(len(raw_message),
                                                           cls.length)
                raise sungrow.BadBinaryMessage(error_msg)
        cls._verify_checksum(raw_message)

    @classmethod
    def _get_digest(cls, raw_message):
        """Compute digest of raw_message
        """
        raise NotImplementedError('deferred to subclasses')

    @classmethod
    def _get_checksum(cls, raw_message):
        """Extract checksum from raw_message
        """
        raise NotImplementedError('deferred to subclasses')

    @classmethod
    def _assert_keys_ok(cls, keys):
        """Confirm that keys match the set of parameter keys
        """
        assert set(keys) == set(cls.names), \
            '{0} != {1}'.format(keys, cls.names)

    @classmethod
    def _raw_to_user_parameters(cls, raw_parameters):
        """Convert raw parameters to user parameters

        Raw parameters are the parameters as extracted directly
        from the native-format message.  They are keyed by raw_keys
        in the class data.
        """
        parameters = dict(raw_parameters)
        for key in cls._discard:
            del parameters[key]
        for key in cls._tenths:
            ## doing this division as a string manipulation
            ##   makes testing easier, because result is the
            ##   same as assigning the decimal number to a
            ##   variable
            int_str = str(parameters[key])
            parameters[key] = float('{0}.{1}'.format(int_str[:-1],
                                                     int_str[-1]))
        for key in cls._ints:
            parameters[key] = int(parameters[key])
        for key in cls._floats:
            parameters[key] = float(parameters[key])
        for key, mapping in cls._mappings.items():
            assert parameters[key] in mapping, \
                '{0} not among {1} in mapping for {2}'.format(parameters[key],
                                                              mapping.keys(),
                                                              key)
            try:
                parameters[key] = mapping[parameters[key]]
            except KeyError:
                err_msg = 'bad value {0} for {1}'.format(parameters[key], key)
                raise sungrow.BadBinaryMessage(err_msg)
        for key, bitfield in cls._bitfields.items():
            byte = parameters.pop(key)
            for bit, bit_key in bitfield.items():
                parameters[bit_key] = bool(byte & (1 << bit))
        return parameters

    def _to_raw_parameters(self):
        """Convert user parameters in message to raw parameters

        Raw parameters are the parameters that translate directly
        into a native-format message.
        """
        raw = dict(self)
        for key in self._tenths:
            raw[key] = int(round(self[key] * 10))
        for key, mapping in self._mappings.items():
            reverse_mapping = dict((value, key)
                                   for key, value in mapping.items())
            raw[key] = reverse_mapping[self[key]]
        for key, bitfield in self._bitfields.items():
            byte = 0
            for bit, bit_key in bitfield.items():
                byte |= (int(raw.pop(bit_key)) << bit)
            raw[key] = byte
        for key, value in self._discard.items():
            raw[key] = value
        return raw

    @classmethod
    def _add_class_data(cls, name, device_type):
        """Add message class data to class

        This involves populating the message length, fields and examples
        and other class attributes.
        """
        device_type_data = sungrow.config.DEVICE_TYPE_DATA[device_type]
        device_example_data = sungrow.config.DEVICE_EXAMPLE_DATA[device_type]
        data = device_type_data['messages'][name]
        cls._data = data
        if 'code' in data:
            cls.code = cls._data['code']
            cls._signature = sungrow.hex_to_bytes(cls.code)
        cls.length = data['length']
        cls.regexp = re.compile(cls.regexp, re.DOTALL | re.MULTILINE)
        cls.fields = data['fields']
        cls.names = [field['name'] for field in cls.fields]
        for key in ('raw_keys',
                    'discard',
                    'tenths', 'ints', 'floats',
                    'mappings', 'bitfields'):
            if key in data:
                private_name = '_{0}'.format(key)
                setattr(cls, private_name, data[key])
        examples = [example for example in device_example_data
                    if example['message_type'] == name]
        for example in examples:
            if 'hex_message' in example:
                hex_message = example['hex_message']
                example['raw_message'] = sungrow.hex_to_bytes(hex_message)
        cls.examples = examples
