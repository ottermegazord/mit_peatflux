"""Test code and data for communicating with Outback charge controller
"""

import sungrow.outback_charge_controller as device_module

import test_sungrow_charge_controller


class TestStatusPage(test_sungrow_charge_controller.TestStatusPage):
    """Tests for status page message
    """

    cls = device_module.StatusPage


class TestDevice(test_sungrow_charge_controller.TestDevice):
    """Test Outback charge controller device
    """

    module = device_module
