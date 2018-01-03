import java.util.HashMap;
import java.util.Map;

class Count {
	int value;
	
	public Count(int value) {
		this.value = value;
	}
	
	@Override
	public boolean equals(Object o) {
		if (o == this) return true;
        if (!(o instanceof Count)) {
            return false;
        }
		Count count = (Count) o;
		return this.value == count.value;
	}
	
	public static void main(String[] args) {
		Map<Count, String> myMap = new HashMap();
		Count count1 = new Count(42);
		myMap.put(count1, "Value");
		Count count2 = new Count(42);
		System.out.println(count1.equals(count2));	// true
		System.out.println(myMap.get(count2));	// null
	}
}
