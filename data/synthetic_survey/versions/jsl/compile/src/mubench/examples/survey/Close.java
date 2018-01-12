package mubench.examples.survey;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.Writer;

public class Close {
	public void missingClose(File file) throws IOException {
		Writer writer = new PrintWriter(new FileOutputStream(file));
		writer.write("foo");
	}
  
	public void missingFinally(File file) throws IOException {
		Writer writer = new PrintWriter(new FileOutputStream(file));
		writer.write("foo");
    writer.close();
	}
}
