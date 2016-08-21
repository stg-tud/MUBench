import java.text.ParseException;

public class SupressError {
	public void misuse() {
		byte[] data = null;
		try {
			data = loadData();
		} catch (Throwable t) {
			data = new byte[0];
		}
		// use data..
	}

	public byte[] loadData() throws ParseException {
		// some time/memory consuming loading process...
		return null;
	}
}