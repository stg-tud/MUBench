from os.path import join, exists
from typing import Optional


class Detector:
    def __init__(self, detectors_path: str, detector_id: str):
        self.id = detector_id
        self.path = join(detectors_path, self.id)
        self.jar_path = join(self.path, self.id + ".jar")
        self.jar_url = "http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/{}.jar".format(self.id)
        self.md5_path = join(self.path, self.id + ".md5")

    @property
    def md5(self) -> Optional[str]:
        md5_file = self.md5_path
        md5 = None

        if exists(md5_file):
            with open(md5_file) as file:
                md5 = file.read()

        return md5

    def __str__(self):
        return self.id
