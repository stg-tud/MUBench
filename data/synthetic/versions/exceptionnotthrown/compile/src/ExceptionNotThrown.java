class ExceptionNotThrown {
	private int x = -1;
	
	public void foo(){
		if (x < 0){
			  new IllegalArgumentException("x must be non-negative");
		}
		else{
			x++;
		}
	}
}
