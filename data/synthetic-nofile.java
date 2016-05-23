import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class NoFile {
	public void misuse(Path path, byte[] content) throws IOException {
		Files.write(path, content);
	}
}
