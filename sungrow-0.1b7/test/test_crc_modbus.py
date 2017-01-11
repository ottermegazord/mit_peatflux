"""Test MODBUS CRC code
"""

from sungrow import modbus


def test_simple_case():
    """Check CRC computation on a simple trial string
    """
    assert modbus.compute_crc(bytearray('123456789')) == 0x4b37


def test_table():
    """Test that cached table matches generated table
    """
    created_table = modbus.create_table()
    assert modbus.TABLE == created_table
