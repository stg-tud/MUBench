import android.app.ProgressDialog;

class DismissShowingDialogOnly {
  void pattern(ProgressDialog dialog) {
		if(dialog.isShowing())
			dialog.dismiss();
  }
}