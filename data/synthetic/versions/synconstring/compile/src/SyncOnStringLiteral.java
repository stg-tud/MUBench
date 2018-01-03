class SyncOnStringLiteral {
	
	private final String LOCK = "LOCK";

	public void foo() {
		synchronized (LOCK) {
			System.out.println(LOCK);
		}
	}
}
