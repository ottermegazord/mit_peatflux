"""Test code and data for communicating with Sungrow inverter
"""

import sungrow.sungrow_inverter as device_module

import test_sungrow_charge_controller


class TestStatusQuery(test_sungrow_charge_controller.TestStatusPage):
    """Tests for status query message
    """

    module = device_module
    cls = device_module.StatusQuery


class TestStatusPage(TestStatusQuery):
    """Tests for status page message
    """

    cls = device_module.StatusPage


class TestDevice(test_sungrow_charge_controller.TestDevice):
    """Test sungrow inverter device
    """

    module = device_module
