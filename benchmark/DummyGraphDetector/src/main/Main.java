package main;

import java.io.File;
import java.io.PrintStream;

public class Main {
	/**
	 * @param args
	 */
	public static void main(String[] args) throws Exception {
		String dirPath = args[0];
		String resultFilePath = args[2];
		System.out.println("Running on: " + dirPath);
		System.out.println("Result  in: " + resultFilePath);

		File resultFile = new File(resultFilePath);
		try (PrintStream writer = new PrintStream(resultFile)) {
			writer.println("digraph {");
			writer.println("0 [label=\"StrBuilder#this#getNullText\"]");
			writer.println("1 [label=\"String#str#length\"]");
			writer.println("0 -> 1");
			writer.println("}");
		}
	}
}
