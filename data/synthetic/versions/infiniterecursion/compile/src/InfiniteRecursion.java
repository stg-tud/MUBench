public class InfiniteRecursion {

	private String foundType;

	public String foundType() {
		return this.foundType();
	}
	
	public static void main(String[] args) {
		 InfiniteRecursion recursionTest = new InfiniteRecursion();
		 recursionTest.foundType();
	}

}