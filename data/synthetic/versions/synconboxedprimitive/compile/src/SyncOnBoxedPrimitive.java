class SyncOnBoxedPrimitive {
	
	private Integer value = 0;
	
	public void foo(){
		  synchronized(value){
			  // some code
			  value++;
			  // some code
		  }
	}
}
