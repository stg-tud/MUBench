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
  
  protected void flushBuffer(byte[] b, int offset, int len) throws IOException {
    // stub
  }
  
  public long length() throws IOException {
    return 0; // stub
  }
}