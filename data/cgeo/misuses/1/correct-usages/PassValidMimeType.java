import android.content.Intent;
import android.net.Uri;

import java.io.File;

class PassValidMimeType {
  void pattern(File file) {
    Intent intent = new Intent();
    intent.setAction(Intent.ACTION_VIEW);
    intent.setDataAndType(Uri.fromFile(file), "image/jpeg");
    return intent;
  }
}