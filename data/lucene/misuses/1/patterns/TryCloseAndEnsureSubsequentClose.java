import java.io.IOException;
import java.io.RandomAccessFile;

import org.apache.lucene.store.BufferedIndexOutput;

class TryCloseAndEnsureSubsequentClose extends BufferedIndexOutput {
  RandomAccessFile file;
  
  public void close() throws IOException {
    try {
      super.close();
    } finally {
      file.close();
    }
  }
}