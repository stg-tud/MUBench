import javax.swing.JFrame;
import javax.swing.SwingUtilities;

public class RunOnEDT {
	public static void main(String[] args) {
		SwingUtilities.invokeLater(new Runnable() {
            public void run() {
            	JFrame f = new JFrame("Main Window");
            	// add components
            	f.pack(); 
            	f.setVisible(true); 
            }
        });
	}
}
