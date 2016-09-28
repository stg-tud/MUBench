from copy import deepcopy
from os.path import join, exists
from typing import Optional, Dict, List


class Detector:
    def __init__(self, detectors_path: str, detector_id: str):
        self.id = detector_id
        self.path = join(detectors_path, self.id)
        self.jar_path = join(self.path, self.id + ".jar")
        self.jar_url = "http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/{}.jar".format(self.id)
        self.md5_path = join(self.path, self.id + ".md5")

        self.files_to_upload = []  # type: List[str]

    @property
    def md5(self) -> Optional[str]:
        md5_file = self.md5_path
        md5 = None

        if exists(md5_file):
            with open(md5_file) as file:
                md5 = file.read()

        return md5

    def specialize_findings(self, findings_path: str, findings: List[Dict[str, str]]) -> List[Dict[str, str]]:
        findings = self._sort_findings(findings)
        for finding in findings:
            self._specialize_finding(findings_path, finding)
        return findings

    def _sort_findings(self, findings: List[Dict[str, str]]) -> List[Dict[str, str]]:
        findings = deepcopy(findings)
        sort_by = self._sort_by
        if sort_by:
            findings.sort(key=lambda f: float(f[sort_by]), reverse=True)
        return findings

    @property
    def _sort_by(self) -> Optional[str]:
        raise NotImplementedError

    def _specialize_finding(self, findings_path: str, finding: Dict[str, str]) -> Dict[str, str]:
        raise NotImplementedError

    def __str__(self):
        return self.id


class DefaultDetector(Detector):
    @property
    def _sort_by(self) -> Optional[str]:
        return None

    def _specialize_finding(self, findings_path: str, finding: Dict[str, str]) -> Dict[str, str]:
        return finding
