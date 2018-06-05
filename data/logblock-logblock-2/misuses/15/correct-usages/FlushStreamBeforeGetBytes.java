import org.logblock.entry.blob.PaintingBlob;
import org.logblock.entry.BlobEntry;

import java.io.ByteArrayOutputStream;
import java.io.DataOutputStream;

class FlushStreamBeforeGetBytes {
  byte[] pattern() throws Exception {
    ByteArrayOutputStream byteOutput = new ByteArrayOutputStream();
    DataOutputStream outStream = new DataOutputStream(byteOutput);
    
    PaintingBlob blobOut = BlobEntry.create(1, PaintingBlob.class);
    blobOut.setArt("artistic");
    blobOut.setDirection((byte) 5);
    blobOut.write(outStream);
    outStream.close();
    
    return byteOutput.toByteArray();
  }
}
