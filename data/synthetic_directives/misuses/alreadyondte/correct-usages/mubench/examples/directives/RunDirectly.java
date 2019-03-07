package mubench.examples.directives;

import javax.swing.JButton;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

public class RunDirectly {
  public void pattern() {
    JButton button = new JButton(":some button:");
    button.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent e) {
        button.setText(":clicked:");
      }
    });
	}
}
