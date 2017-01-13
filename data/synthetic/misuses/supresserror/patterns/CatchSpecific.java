import java.text.ParseException;

public class CatchSpecific {
	public void pattern(Target target) {
		byte[] data = null;
		try {
			data = target.loadData();
		} catch (ParseException t) {
			data = new byte[0];
		}
		// use data..
	}
}
