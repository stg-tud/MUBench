import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

public class Force {
  public void pattern(ByteBuffer content, Path path) throws IOException {
    FileChannel out = FileChannel.open(path, StandardOpenOption.WRITE);
    out.write(content);
    out.force(false);
  }
}
