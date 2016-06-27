import com.actionbarsherlock.app.SherlockActivity;

class CallSuperOnDestroy extends SherlockActivity {
  @Override
  onDestroy() {
  	super.onDestroy();
    // do other cleanup...
  }
}