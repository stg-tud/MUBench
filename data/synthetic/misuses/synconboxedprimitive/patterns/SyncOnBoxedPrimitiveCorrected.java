class SyncOnBoxedPrimitiveCorrected {
	
	private Integer value = 0;
	
	public void foo(){
		  synchronized(this){
			  // some code
			  value++;
			  // some code
		  }
	}
}
