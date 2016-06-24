import android.content.Context;
import android.content.res.TypedArray;
import android.util.AttributeSet;

class HandleException {
  String pattern(Context context, AttributeSet attrs, int attributeId) {
    TypedArray typedArray = context.obtainStyledAttributes(attrs, new int[]{attributeId});
    try {
      return typedArray.getString(0);
    } catch (Exception ignore) {
      // Failed for some reason.
      return null;
    }
  }
}