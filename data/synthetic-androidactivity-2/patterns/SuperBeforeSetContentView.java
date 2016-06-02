import android.app.Activity;
import android.os.Bundle;

public class C extends Activity {
	@Override
	protected void onCreate(Bundle state) {
		super.onCreate(state); // <-- required before setContentView
		setContentView(R.layout.main);
    findViewById(R.id.editText1);
	}
}
