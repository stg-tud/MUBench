package mubench.examples.survey;

import javax.swing.JFrame;

public class JFramePack {
  
	public void needsPackToLayout(JFrame f) {
		f.setVisible(true);
	}
  
	public void packAfterShowHasNoEffect(JFrame f) {
		f.setVisible(true);
		f.pack();
	}
}
