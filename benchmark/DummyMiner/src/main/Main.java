package main;

import java.io.File;
import java.io.PrintStream;
import java.util.LinkedList;

public class Main {
	/**
	 * @param args
	 */
	public static void main(String[] args) throws Exception {
		String dirPath = args[0];
		String resultFilePath = args[1];
		System.out.println("Running on: " + dirPath);
		System.out.println("Result  in: " + resultFilePath);

		File resultFile = new File(resultFilePath);
		try (PrintStream writer = new PrintStream(resultFile)) {
			for (File file : listFiles(dirPath)) {
				writer.println("file: " + file.getAbsolutePath());
				writer.println("---");
			}
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
