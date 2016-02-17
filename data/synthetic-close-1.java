import org.apache.commons.io.IOUtils;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.Writer;

public class Close {
	public void misuse(OutputStream out) throws IOException {
		PrintWriter writer = new PrintWriter(out);
		writer.write("foo");
	}
	
	public void tryWithResources(OutputStream out) throws IOException {
		try (Writer writer = new PrintWriter(out)) {
			writer.write("foo");
		}
	}

	public void close(OutputStream out) throws IOException {
		Writer writer = null;
		try {
			writer = new PrintWriter(out);
			writer.write("foo");
		} finally {
			if (writer != null) {
				writer.close();
			}
		}
	}
	
	public void ioUtils(OutputStream out) throws IOException {
		Writer writer = null;
		try {
			writer = new PrintWriter(out);
			writer.write("foo");
		} finally {
			IOUtils.closeQuietly(writer);
		}
	}
}
