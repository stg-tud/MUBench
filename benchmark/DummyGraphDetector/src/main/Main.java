package main;

import java.io.File;
import java.io.PrintStream;

import de.tu_darmstadt.stg.mubench.cli.ArgParser;
import de.tu_darmstadt.stg.mubench.cli.DetectorArgs;

public class Main {
	/**
	 * @param args
	 */
	public static void main(String[] args) throws Exception {
		DetectorArgs myArgs = ArgParser.parse(args);
		String dirPath = myArgs.projectSrcPath;
		String resultFilePath = myArgs.findingsFile;
		
		System.out.println("Running on: " + dirPath);
		System.out.println("Result  in: " + resultFilePath);

		File resultFile = new File(resultFilePath);
		try (PrintStream writer = new PrintStream(resultFile)) {
			writer.println("graph: >");
			writer.println("  digraph {");
			writer.println("    0 [label=\"StrBuilder#this#getNullText\"]");
			writer.println("    1 [label=\"String#str#length\"]");
			writer.println("    0 -> 1");
			writer.println("  }");
		}
	}
}
