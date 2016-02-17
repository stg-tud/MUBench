import java.awt.Dimension;
import javax.swing.JFrame;

public class Pack1 {
	public void misuse(JFrame f, Dimension d) {
		f.pack();
		f.setPreferredSize(d);
	}
  
	public void pack(JFrame f, Dimension d) {
		f.setPreferredSize(d);
		f.pack();
	}
}
