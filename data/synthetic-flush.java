import java.io.File;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;

public class ChannelFlush {
	public void misuse(ByteBuffer content) throws IOException {
		Path path = new File("foo").toPath();
		
		FileChannel out = FileChannel.open(path, StandardOpenOption.WRITE);
		out.write(content);
		
		FileChannel in = FileChannel.open(path, StandardOpenOption.READ);
		in.read(content);
	}
}
