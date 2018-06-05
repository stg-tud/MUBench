import android.content.Intent;
import org.gnucash.android.ui.UxArgument;

class GetStringParameterAsString {
  String pattern(Intent intent) {
    return intent.getStringExtra(UxArgument.SELECTED_ACCOUNT_UID);
  }
}