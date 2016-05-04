import unittest
from configparser import ConfigParser
from os import listdir

from os.path import realpath, join, dirname, pardir


class DetectorConfigurationsTest(unittest.TestCase):
    def setUp(self):
        mubench_dir = realpath(join(dirname(__file__), pardir, pardir, pardir))
        detector_dir = join(mubench_dir, 'detectors')
        self.available_configs = [join(detector_dir, detector, detector + '.cfg') for detector in listdir(detector_dir)]
        self.parser = ConfigParser()

    def test_default_section_configured(self):
        for detector_config in self.available_configs:
            self.parser.read(detector_config)
            self.assertIsNotNone(self.parser["DEFAULT"])

    def test_result_files_configured(self):
        for detector_config in self.available_configs:
            self.parser.read(detector_config)
            self.assertIsNotNone(self.parser["DEFAULT"]["Result File"])


if __name__ == '__main__':
    unittest.main()
