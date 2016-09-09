package main;

import java.io.File;
import java.util.LinkedList;

import de.tu_darmstadt.stg.mubench.cli.ArgParser;
import de.tu_darmstadt.stg.mubench.cli.DetectorArgs;
import de.tu_darmstadt.stg.mubench.cli.DetectorOutput;

public class Main {
	/**
	 * @param args
	 */
	public static void main(String[] args) throws Exception {
		DetectorArgs myArgs = ArgParser.parse(args);
		
		String dirPath = myArgs.getTargetSrcPath();
		String findingsFile = myArgs.getFindingsFile();
		
		DetectorOutput output = new DetectorOutput(findingsFile);
		for (File file : listFiles(dirPath)) {
			output.add(file.getPath(), "<init>()");
		}
		output.write();
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
