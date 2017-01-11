"""Testing of device objects
"""

import datetime

import sungrow.device
import sungrow.sungrow_charge_controller


class TestDevice(object):
    """Testing of device objects
    """
    def __init__(self):
        self.device = sungrow.device.Device()

    def test_log_to_file(self):
        """

        The device-class-specific test code deals with testing logging to
        streams; this exercises logging to a file.
        """
        import datetime
        import os
        import os.path
        import tempfile

        timestamp = datetime.datetime(year=2012, month=6, day=12)
        expected = '2012-06-12 00:00:00'

        message = sungrow.sungrow_charge_controller.StatusQuery()
        fid, file_name = tempfile.mkstemp(suffix='.log')
        try:
            device = sungrow.device.Device(data_streams={'dummy': file_name})
            device.log_data['dummy'](message, timestamp)
            written = open(file_name).read().strip()
            assert written == expected, '{0} != {1}'.format(written,
                                                            expected)
        finally:
            os.close(fid)
            if os.path.exists(file_name):
                os.remove(file_name)
