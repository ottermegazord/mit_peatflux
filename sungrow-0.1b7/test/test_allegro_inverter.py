"""Test code for Allegro inverter device and messages
"""

import sungrow.allegro_inverter as device_module

import test_sungrow_charge_controller


class TestStatusPage(test_sungrow_charge_controller.TestStatusPage):
    """Tests for status query message
    """

    module = device_module
    cls = device_module.StatusPage    

class TestEnableRemote(TestStatusPage):
    """Tests for enable_remote message
    """

    module = device_module
    cls = device_module.EnableRemote


class TestDisableRemote(TestStatusPage):
    """Tests for disable_remote message
    """

    module = device_module
    cls = device_module.DisableRemote


class TestSetStandbyLevel(TestStatusPage):
    """Tests for set_standby_level message
    """

    module = device_module
    cls = device_module.SetStandbyLevel
