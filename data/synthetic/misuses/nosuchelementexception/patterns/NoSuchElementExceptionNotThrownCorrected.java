import java.util.Iterator;
import java.util.NoSuchElementException;

class NoSuchElementExceptionNotThrownCorrected implements Iterator<Integer> {
	
	@Override
	public boolean hasNext() {
		return false;
	}

	@Override
	public Integer next() {
		if (!hasNext()) {
			throw new NoSuchElementException();
		}
		return null;
	}

	@Override
	public void remove() {
		System.out.println("remove element");
	}
}
