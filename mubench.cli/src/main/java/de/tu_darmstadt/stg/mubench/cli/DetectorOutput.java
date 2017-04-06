package de.tu_darmstadt.stg.mubench.cli;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.UnsupportedEncodingException;
import java.io.Writer;
import java.util.*;

import org.yaml.snakeyaml.DumperOptions;
import org.yaml.snakeyaml.Yaml;

@SuppressWarnings("WeakerAccess")
public class DetectorOutput {
	private final File findingsFile;
	private final File runInformationFile;
	private final List<DetectorFinding> findings;
	private final HashMap<String, Object> runInformation;

	DetectorOutput(String findingsFilePath, String runInformationFilePath) throws FileNotFoundException {
		findings = new LinkedList<>();
		runInformation = new HashMap<>();
		findingsFile = new File(findingsFilePath);
		runInformationFile = new File(runInformationFilePath);
	}

	/**
	 * @return directory to write additional output to, e.g., for debugging purposes.
	 * @throws FileNotFoundException if the path cannot be determined
	 */
	@SuppressWarnings("unused")
    public String getAdditionalOutputPath() throws FileNotFoundException {
		return findingsFile.getParent();
	}

    /**
     * Add a finding to the output.
     * @param file the finding's file location
     * @param method the findings's method location
     * @return the new finding
     */
	public DetectorFinding add(String file, String method) {
		DetectorFinding finding = new DetectorFinding(findings.size(), file, method);
		findings.add(finding);
		return finding;
	}

    /**
     * Add data about the detector run to the output.
     * @param key identifier of the data
     * @param value value of the data
     */
	public void addRunInformation(String key, String value) {
		runInformation.put(key, value);
	}

    /**
     * Add data about the detector run to the output.
     * @param key identifier of the data
     * @param values values of the data
     */
	@SuppressWarnings({"unchecked", "unused"})
	public void addRunInformation(String key, Iterable<String> values) {
		runInformation.put(key, values);
	}

	void write() throws IOException {
		writeFindings();
		writeRunInformation();
	}

	private void writeFindings() throws IOException {
		try (Writer writer = new OutputStreamWriter(new FileOutputStream(findingsFile), "UTF-8")) {
			DumperOptions options = new DumperOptions();
			options.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK);
			Yaml yaml = new Yaml(options);
			yaml.dumpAll(getContent(), writer);
		}
	}

	private Iterator<Map<String, Object>> getContent() {
		List<Map<String, Object>> content = new ArrayList<>();
		for (DetectorFinding finding : findings) {
			content.add(finding.getContent());
		}
		return content.iterator();
	}

	private void writeRunInformation() throws IOException {
		try (Writer writer = new OutputStreamWriter(new FileOutputStream(runInformationFile), "UTF-8")) {
			DumperOptions options = new DumperOptions();
			options.setDefaultFlowStyle(DumperOptions.FlowStyle.BLOCK);
			Yaml yaml = new Yaml(options);
			yaml.dump(runInformation, writer);
		}
	}
}
