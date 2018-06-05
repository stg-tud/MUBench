import android.app.ListFragment;

class CheckAddedBeforeAccess {
  void pattern(ListFragment lf, int position) {
    if (lf.isAdded() && lf.getListView() != null) {
      lf.getListView().setSelectionFromTop(position, 0);
    }
  }
}