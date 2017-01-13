import java.io.IOException;
import java.io.File;

class EnsureDirectoryExistsBeforeCreateFile {
  void pattern(File lockDir, String lockFilename) throws IOException {
    File lockFile = new File(lockDir, lockFilename);
    if (!lockDir.exists()) {
      if (!lockDir.mkdirs()) {
        throw new IOException("Cannot create lock directory: " + lockDir);
      }
    }
    lockFile.createNewFile();
  }
}
