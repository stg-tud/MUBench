import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

public class FISExists {
	public void misuse(File file) throws IOException {
		try (FileInputStream fis = new FileInputStream(file)) {
		  // do something with fis...
		}
	}
}
