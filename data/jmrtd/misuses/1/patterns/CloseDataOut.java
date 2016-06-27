import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;
import java.io.IOException;

import sos.mrtd.Util;

class CloseDataOut {
  void pattern(byte[] rapdu, long ssc) throws IOException {
    ByteArrayOutputStream out = new ByteArrayOutputStream();
    DataOutputStream dataOut = new DataOutputStream(out);
    dataOut.writeLong(ssc);
    byte[] paddedData = Util.pad(rapdu, 0, rapdu.length - 2 - 8 - 2);
    dataOut.write(paddedData, 0, paddedData.length);
    dataOut.flush();
    dataOut.close();
  }
}