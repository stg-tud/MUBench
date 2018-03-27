package mubench.examples.survey;

import javax.swing.JFrame;

public class PackBeforeVisible {
	public void pattern(JFrame f) {
		f.pack();
		f.setVisible(true);
	}
}
