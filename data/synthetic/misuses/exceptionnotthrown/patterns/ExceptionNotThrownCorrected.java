class ExceptionNotThrownCorrected {
	private int x = -1;
	
	public void foo(){
		if (x < 0){
			  throw new IllegalArgumentException("x must be non-negative");
		}
		else{
			x++;
		}
	}
}
