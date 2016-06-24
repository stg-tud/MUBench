import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.EnumSet;

public class ByteBufferFlip {
  public void misuse(byte[] result) throws IOException {
  		ByteBuffer buffer = ByteBuffer.allocate(result.length);
  		buffer.put(result);
  		// missing buffer.flip() for subsequent reading
		
  		Path fp = FileSystems.getDefault().getPath("output.file");
  		FileChannel outChannel = FileChannel
  				.open(fp, EnumSet.of(StandardOpenOption.CREATE,
  						StandardOpenOption.TRUNCATE_EXISTING,
  						StandardOpenOption.WRITE));

  		outChannel.write(buffer); // <-- reads buffer
  		outChannel.force(false);
  	}
}
