import javax.swing.JButton;
import javax.swing.SwingUtilities;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;

public class UpdateUI {
  public void misuse() {
    JButton button = new JButton(":some button:");
    button.addActionListener(new ActionListener() {
      public void actionPerformed(ActionEvent e) {
        SwingUtilities.invokeLater(new Runnable() {
          public void run() {
            button.setText(":clicked:");
          }
        });
      }
    });
	}
}
