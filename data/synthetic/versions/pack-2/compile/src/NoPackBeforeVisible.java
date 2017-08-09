import javax.swing.JFrame;

public class NoPackBeforeVisible {
	public void misuse(JFrame f) {
		f.setVisible(true);
	}
}
