import java.io.IOException;
import java.io.File;

class EnsureDirectoryExistsBeforeCreateFile {
  boolean obtain(File lockDir, String lockFilename) throws IOException {
    File lockFile = new File(lockDir, lockFilename);
    if (!lockDir.exists()) {
      if (!lockDir.mkdirs()) {
        throw new IOException("Cannot create lock directory: " + lockDir);
      }
    }
    return lockFile.createNewFile();
  }
}