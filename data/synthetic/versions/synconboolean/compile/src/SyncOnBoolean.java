class SyncOnBoolean {
	
	private static Boolean flag = Boolean.TRUE;
	
	public void foo(){
		  synchronized(flag){
			  if(!flag){
				  System.out.println("true condition");
			  }else{
				  System.out.println("false condition");
			  }		  
		  }
	}
}
