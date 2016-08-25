import java.util.HashMap;

public class Synchronized {
	private HashMap<String, String> map;
	
	public void onEvent(String sender, String event) {
		synchronized (map) {
			map.put(sender, event);
		}
	}
}
