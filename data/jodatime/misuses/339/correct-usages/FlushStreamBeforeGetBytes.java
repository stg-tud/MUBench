import java.io.ByteArrayOutputStream;
import java.io.DataOutput;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.OutputStream;

class FlushStreamBeforeGetBytes {
  void pattern(OutputStream out) throws IOException {
    if (out instanceof DataOutput) {
      DataOutput dout = (DataOutput) out;
      dout.writeByte('F');
    } else {
      DataOutputStream dout = new DataOutputStream(out);
      dout.writeByte('F');
      dout.flush();
    }
  }
}
