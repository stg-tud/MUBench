import java.text.ParseException;

public class CatchSpecific {
	public void pattern() {
		byte[] data = null;
		try {
			data = loadData();
		} catch (ParseException t) {
			data = new byte[0];
		}
		// use data..
	}

	public byte[] loadData() throws ParseException {
		// some time/memory consuming loading process...
		return null;
	}
}