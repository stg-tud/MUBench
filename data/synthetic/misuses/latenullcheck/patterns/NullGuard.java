public class NullGuard {
	public void pattern(Object o) {
		if (o == null) {
			o = new Object();
		}
		o.hashCode();
	}
}
