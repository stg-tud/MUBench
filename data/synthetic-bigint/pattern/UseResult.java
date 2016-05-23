import java.math.BigInteger;

public class UseResult {	
	public void pattern(String value, int bit) {
		BigInteger i = new BigInteger(value);
		i = i.setBit(bit);
		return i;
	}
}
