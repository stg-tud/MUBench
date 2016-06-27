import org.apache.jackrabbit.server.io.IOManager;
import org.apache.tika.metadata.Metadata;

import java.io.IOException;

class CheckIOManagerForNull{
  String detect(IOManager ioManager, Metadata metadata) throws IOException {
    if (ioManager != null && ioManager.getDetector() != null) {
      return ioManager.getDetector().detect(null, metadata).toString();
    } else {
      return "application/octet-stream";
    }
  }
}