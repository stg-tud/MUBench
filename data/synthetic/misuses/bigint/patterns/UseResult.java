import java.math.BigInteger;

public class UseResult {	
	public BigInteger pattern(String value, int bit) {
		BigInteger i = new BigInteger(value);
		i = i.setBit(bit);
		return i;
	}
}
