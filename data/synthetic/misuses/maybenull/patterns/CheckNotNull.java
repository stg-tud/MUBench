public class CheckNotNull {
	public void pattern(Object maybeNull) {
    if (maybeNull != null) {
      maybeNull.hashCode();
    }
	}
}
