import java.math.BigInteger;

public class BigInt {
	public BigInteger misuse() {
		BigInteger i = new BigInteger("42");
		i.setBit(5);
		return i;
	}
}
