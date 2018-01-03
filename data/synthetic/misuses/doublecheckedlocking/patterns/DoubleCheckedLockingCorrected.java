public class DoubleCheckedLockingCorrected {

	private volatile Object resource = null;
	public Object getResource() {
        if (resource == null) {
            synchronized(this) {
                if (resource == null)
                    resource = new Object();
            }
        }
        return resource;
    }
     
	// other functions and members...
}
