import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.Writer;

public class TryFinallyClose {
	public void pattern(OutputStream out, String value) throws IOException {
		Writer writer = null;
		try {
			writer = new PrintWriter(out);
			writer.write(value);
		} finally {
			if (writer != null) {
				writer.close();
			}
		}
	}
}
