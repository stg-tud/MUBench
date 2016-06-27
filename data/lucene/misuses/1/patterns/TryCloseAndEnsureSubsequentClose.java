
class TryCloseAndEnsureSubsequentClose extends BufferedIndexOutput {
  RandomAccessFile file;
  
  @Override
  void close() throws IOException {
    try {
      super.close();
    } finally {
      file.close();
    }
  }
}