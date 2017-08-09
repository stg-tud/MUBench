import java.awt.Dimension;
import javax.swing.JFrame;

public class PackAfterVisible {
	public void misuse(JFrame f, Dimension d) {
		f.setVisible(true);
		f.pack();
	}
}
