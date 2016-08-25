public class Deadlock {
	public void misuse(Object o) {
		synchronized (o) {
			o.hashCode();
			synchronized (o) {
				o.hashCode();
			}
		}
	}
}
