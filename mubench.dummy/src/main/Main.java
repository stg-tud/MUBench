package main;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.LinkedList;

import de.tu_darmstadt.stg.mubench.cli.CodePath;
import de.tu_darmstadt.stg.mubench.cli.DetectorArgs;
import de.tu_darmstadt.stg.mubench.cli.DetectorOutput;
import de.tu_darmstadt.stg.mubench.cli.MuBenchRunner;

public class Main extends MuBenchRunner {

	public static void main(String[] args) throws Exception {
		new Main().run(args);
	}

	@Override
	protected void mineAndDetect(DetectorArgs args, DetectorOutput output) throws FileNotFoundException {
		dummyMine(output, args.getTargetPath().srcPath);
	}

	@Override
	protected void detectOnly(DetectorArgs args, DetectorOutput output) throws FileNotFoundException {
		dummyMine(output, args.getTargetPath().srcPath);
	}

	private void dummyMine(DetectorOutput output, String targetPath) {
		for (File file : listFiles(targetPath)) {
			output.add(file.getPath(), "m()");
		}
	}

	private static LinkedList<File> listFiles(String directoryName) {
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
