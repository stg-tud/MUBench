public class Synchronized {
	public void pattern(Object o) {
		synchronized (o) {
			o.hashCode();
			o.hashCode();
		}
	}
}
