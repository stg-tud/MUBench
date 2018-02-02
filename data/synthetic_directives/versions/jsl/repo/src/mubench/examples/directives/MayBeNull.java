package mubench.examples.directives;

public class MayBeNull {
	public void misuse(Object maybeNull) {
    if (maybeNull == null) {
      maybeNull.hashCode();
    }
	}
}
