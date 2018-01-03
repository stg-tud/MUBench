class SyncOnStringLiteralCorrected {
	
	private final String LOCK = "LOCK";

	public void foo() {
		synchronized (this) {
			System.out.println(LOCK);
		}
	}
}
