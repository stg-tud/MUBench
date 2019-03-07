import android.text.Editable;
import org.wordpress.android.util.WPEditText;

class CheckTextNull {
  void pattern(WPEditText mContentEditText, int mSelectionEnd) {
    Editable str = mContentEditText.getText();
    if (str != null) {
      if (mSelectionEnd > str.length())
        mSelectionEnd = str.length();
      str.insert(mSelectionEnd, "\n<!--more-->\n");
    }
  }
}