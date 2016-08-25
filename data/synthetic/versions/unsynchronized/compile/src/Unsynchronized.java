import java.util.HashMap;

public class Unsynchronized {
	private HashMap<String, String> map;
	
	public void onEvent(String sender, String event) {
			map.put(sender, event);
	}
}
