import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

public class CheckFileExists {
	public void pattern(File file) throws IOException {
		if (file.exists()) {
			try (FileInputStream fis = new FileInputStream(file)) {
        // do something with fis...
      }
		}
	}
}
