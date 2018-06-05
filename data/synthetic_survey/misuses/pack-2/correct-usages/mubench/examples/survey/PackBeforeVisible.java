package mubench.examples.survey;

import java.awt.Dimension;
import javax.swing.JFrame;

public class PackBeforeVisible {
	public void pattern(JFrame f, Dimension d) {
		f.pack();
		f.setVisible(true);
	}
}
