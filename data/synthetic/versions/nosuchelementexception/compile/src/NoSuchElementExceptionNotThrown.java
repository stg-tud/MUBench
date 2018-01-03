import java.util.Iterator;

public class NoSuchElementExceptionNotThrown implements Iterator<Integer> {

	@Override
	public boolean hasNext() {
		return false;
	}

	@Override
	public Integer next() {
		return null;
	}

	@Override
	public void remove() {
		System.out.println("remove element");
	}

}