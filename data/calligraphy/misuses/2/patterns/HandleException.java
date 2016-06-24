import android.content.Context;
import android.content.res.Resources;
import android.content.res.TypedArray;
import android.util.TypedValue;

class HandleException {
  String pattern(Context context, int styleId, int attributeId) {
    Resources.Theme theme = context.getTheme();
    TypedValue value = new TypedValue();
    theme.resolveAttribute(styleId, value, true);
    TypedArray typedArray = theme.obtainStyledAttributes(value.resourceId, new int[]{attributeId});
    try {
      return typedArray.getString(0);
    } catch (Exception ignore) {
      // Failed for some reason.
      return null;
    }
  }
}