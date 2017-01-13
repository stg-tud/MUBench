import org.apache.jackrabbit.server.io.IOManager;
import org.apache.tika.detect.Detector;
import org.apache.tika.metadata.Metadata;

import java.io.IOException;

class CheckIOManagerForNull{
  void detect(IOManager ioManager, Metadata metadata) throws IOException {
    Detector detector = ioManager.getDetector();
    if (detector != null) {
      detector.detect(null, metadata);
    }
  }
}
