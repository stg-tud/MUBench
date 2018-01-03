public class NonExistingCloneCorrected {

	private int aVar;

	public NonExistingCloneCorrected(int avar) {
		this.aVar = avar;
	}

	// other methods
	
	@Override
	protected Object clone() {
		NonExistingCloneCorrected nonExistingCloneCorrected = null;
		try {
			nonExistingCloneCorrected = (NonExistingCloneCorrected) super.clone();
		} catch (CloneNotSupportedException e) {
			e.printStackTrace();
		}
		return nonExistingCloneCorrected;
	}
}
