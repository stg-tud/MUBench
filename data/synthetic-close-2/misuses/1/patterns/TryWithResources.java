import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.Writer;

public class TryWithResources {
	public void pattern(OutputStream out, String value) throws IOException {
		try (Writer writer = new PrintWriter(out)) {
			writer.write(value);
		}
	}
}
