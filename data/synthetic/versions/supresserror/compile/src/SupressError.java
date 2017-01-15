public class SupressError {
	public void misuse(Target target) {
		byte[] data = null;
		try {
			data = target.loadData();
		} catch (Throwable t) {
			data = new byte[0];
		}
		// use data..
	}
}
