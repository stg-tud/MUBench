package main;

import java.io.File;
import java.io.FileWriter;
import java.nio.file.Paths;
import java.util.LinkedList;

public class Main {
	/**
	 * @param args
	 */
	public static void main(String[] args) throws Exception {
		String dirPath = args[0];
		String resultPath = args[1];
		System.out.println("Running on: " + dirPath);
		System.out.println("Result  in: " + resultPath);

		LinkedList<File> files = listFiles(dirPath);

		File resultFile = Paths.get(resultPath, "result.txt").toFile();
		try (FileWriter writer = new FileWriter(resultFile)) {
			for (File file : files) {
				writer.write("File: " + file.getAbsolutePath());
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
