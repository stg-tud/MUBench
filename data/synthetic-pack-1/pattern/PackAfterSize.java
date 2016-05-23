import java.awt.Dimension;
import javax.swing.JFrame;

public class PackAfterSize {
	public void pattern(JFrame f, Dimension d) {
		f.setPreferredSize(d);
		f.pack();
	}
}
