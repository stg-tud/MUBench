public class FlippedNull {
	public void misuse(Object maybeNull) {
    if (maybeNull == null) {
      maybeNull.hashCode();
    }
	}
}
