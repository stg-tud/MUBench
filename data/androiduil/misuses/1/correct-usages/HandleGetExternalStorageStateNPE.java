import android.os.Environment;

class HandleGetExternalStorageStateNPE {
  String pattern() {
    try {
    	return Environment.getExternalStorageState();
    } catch (NullPointerException e) {
    	return "";
    }
  }
}