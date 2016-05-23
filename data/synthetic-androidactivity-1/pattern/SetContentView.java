import android.app.Activity;
import android.os.Bundle;

public class SetContentView extends Activity {
  @Override
  protected void onCreate(Bundle state) {
    super.onCreate(state);
    setContentView(R.layout.main); // <-- required for findViewById to succeed
    findViewById(R.id.editText1);
  }
}
