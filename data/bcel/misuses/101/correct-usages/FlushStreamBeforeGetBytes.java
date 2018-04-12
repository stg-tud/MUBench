import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;

import org.apache.commons.bcel6.generic.Instruction;

class FlushStreamBeforeGetBytes {
  byte[] pattern(Instruction i) {
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    DataOutputStream dos = new DataOutputStream(baos);
    try {
      i.dump(dos);
      dos.flush();
    } catch (IOException e) {
      return new byte[0];
    }
    return baos.toByteArray();
  }
}
