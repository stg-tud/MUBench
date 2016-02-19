import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;

public class FISExists {

	public void misuse(String path) throws IOException {
		File file = new File(path);
		FileInputStream fis = new FileInputStream(file);
		fis.close();
	}

	public void exists(String path) throws IOException {
		File file = new File(path);
		if (file.exists()) {
			FileInputStream fis = new FileInputStream(file);
			fis.close();
		}
	}
}