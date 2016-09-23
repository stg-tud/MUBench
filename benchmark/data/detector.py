from os.path import join, exists
from typing import Optional

from benchmark.data.experiment import Experiment


class Detector:
    def __init__(self, detectors_base_path: str, id: str):
        self.id = id
        self.__detectors_base_path = detectors_base_path
        self.__base_path = join(self.__detectors_base_path, self.id)
        self.jar_path = join(self.__base_path, self.id + ".jar")
        self.jar_url = "http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/{}.jar".format(self.id)
        self.md5_path = join(self.__base_path, self.id + ".md5")

    @property
    def md5(self) -> Optional[str]:
        md5_file = self.md5_path
        md5 = None

        if exists(md5_file):
            with open(md5_file) as file:
                md5 = file.read()

        return md5

    def get_findings_path(self, findings_base_path: str, experiment: Experiment):
        return join(experiment.findings_path(findings_base_path), self.id)