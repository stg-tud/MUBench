import javax.swing.JFrame;

public class PackAfterVisible {
	public void misuse(JFrame f) {
		f.setVisible(true);
		f.pack();
	}
}
