"""Testing of utilities and the like
"""

import sungrow
import sungrow.config


def test_hex_bytes():
    """Test conversion to and from hex
    """
    example_data = sungrow.config.DEVICE_EXAMPLE_DATA
    examples = sum(([value['hex_message']
                     for value in example if 'hex_message' in value]
                    for example in example_data.values()), [])
    for example in examples:
        normalized = ' '.join(example.split())
        weird_whitespace = example.replace(' ', '\n')
        bytestring = sungrow.hex_to_bytes(weird_whitespace)
        bytea = sungrow.hex_to_bytearray(normalized)
        assert bytea == bytestring
        hex_again = sungrow.bytes_to_hex(bytestring)
        assert hex_again == normalized
