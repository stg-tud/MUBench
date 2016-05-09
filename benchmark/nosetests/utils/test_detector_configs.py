from configparser import ConfigParser
from os import listdir
from os.path import join
from os.path import realpath, dirname, pardir

available_configs = []


def setup_module(module):
    mubench_dir = realpath(join(dirname(__file__), pardir, pardir, pardir))
    detector_dir = join(mubench_dir, 'detectors')
    module.available_configs = [join(detector_dir, detector, detector + '.cfg') for detector in listdir(detector_dir)]
    assert module.available_configs, "No configs found!"


def test_result_files_configured():
    for detector_config in available_configs:
        parser = ConfigParser()
        parser.read(detector_config)
        parser["DEFAULT"]["Result File"]