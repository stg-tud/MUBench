import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

public class FileCreate {
	public void pattern(Path path, byte[] content) throws IOException {
		Files.write(path, content, StandardOpenOption.CREATE);
	}
}
