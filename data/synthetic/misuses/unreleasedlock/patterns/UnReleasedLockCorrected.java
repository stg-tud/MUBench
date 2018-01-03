import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

class UnReleasedLockCorrected {
	
	private final Lock activationLock = new ReentrantLock();

	public void foo() {
		try {
			activationLock.lock();
			System.out.println("lock acquired");
		} catch (Exception ex) {
			ex.printStackTrace();
		}finally {
			if (activationLock != null)
				activationLock.unlock();
		}
	}
}
