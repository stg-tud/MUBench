import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

public class NoFile {

	public void misuse(Path path, byte[] content) throws IOException {
		Files.write(path, content);
	}
	
	public void createOption(Path path, byte[] content) throws IOException {
		Files.write(path, content, StandardOpenOption.CREATE);
	}
}