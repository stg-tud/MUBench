import android.app.Activity;
import android.os.Bundle;
import android.widget.EditText;

public class ActivityDelegateCreateTooLate extends Activity {
  private EditText mEditText;

  @Override
  protected void onCreate(Bundle state) {
    setContentView(R.layout.main);
    super.onCreate(state); // <-- required before setContentView()
    String someText = ":some saved text:";
    mEditText = (EditText) findViewById(R.id.editText1);
    mEditText.setText(someText);
  }
}
