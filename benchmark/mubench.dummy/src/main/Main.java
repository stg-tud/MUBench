package main;

import java.io.File;
import java.io.IOException;
import java.util.LinkedList;

import de.tu_darmstadt.stg.mubench.cli.CodePath;
import de.tu_darmstadt.stg.mubench.cli.DetectorOutput;
import de.tu_darmstadt.stg.mubench.cli.MuBenchRunner;

public class Main extends MuBenchRunner {

	public static void main(String[] args) throws IOException {
		new Main().run(args);
	}
	
	protected void mineAndDetect(CodePath trainingAndTargetPath, DetectorOutput output) {
		dummyMine(output, trainingAndTargetPath.srcPath);
	}
	
	protected void detectOnly(CodePath patternPath, CodePath targetPath, DetectorOutput output) {
		dummyMine(output, targetPath.srcPath);
	}

	private void dummyMine(DetectorOutput output, String targetPath) {
		for (File file : listFiles(targetPath)) {
			output.add(file.getPath(), "m()");
		}
	}

	public static LinkedList<File> listFiles(String directoryName) {
		LinkedList<File> files = new LinkedList<File>();
		File directory = new File(directoryName);

		// get all the files from a directory
		File[] fList = directory.listFiles();
		for (File file : fList) {
			if (file.isFile()) {
				files.add(file);
			} else if (file.isDirectory()) {
				files.addAll(listFiles(file.getAbsolutePath()));
			}
		}

		return files;
	}
}
