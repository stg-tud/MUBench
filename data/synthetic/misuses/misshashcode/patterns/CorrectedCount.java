import java.util.HashMap;
import java.util.Map;

class CorrectedCount {
	int value;

	public CorrectedCount(int value) {
		this.value = value;
	}

	@Override
	public boolean equals(Object o) {
		if (o == this)
			return true;
		if (!(o instanceof CorrectedCount)) {
			return false;
		}
		CorrectedCount count = (CorrectedCount) o;
		return this.value == count.value;
	}

	@Override
	public int hashCode() {
		int result = 17;
		result = 31 * result + value;
		return result;
	}
	
	public static void main(String[] args) {
		Map<CorrectedCount, String> myMap = new HashMap();
		CorrectedCount count1 = new CorrectedCount(42);
		myMap.put(count1, "Value");
		CorrectedCount count2 = new CorrectedCount(42);
		System.out.println(count1.equals(count2));	// true
		System.out.println(myMap.get(count1));	// Value
	}
}
