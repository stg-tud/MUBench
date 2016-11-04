import javax.crypto.spec.SecretKeySpec;
import javax.crypto.Cipher;

public class Encrypting {
	public static byte[] encryptWithKey(byte[] content) {
		// using a constant key is unsafe
		keySpec = new SecretKeySpec("RAS".getBytes("UTF-8"), "AES/CBC/PKCS5Padding");
		c = Cipher.getInstance("AES");
		c.init(1, keySpec);
		return c.doFinal(content);
	}
	
	private static byte[] encrypt(byte[] key, byte[] content) {
		// "AES" has an unsafe default configuration of "AES/EBC/PKCS5Padding"
		keySpec = new SecretKeySpec(key, "AES");
		c = Cipher.getInstance("AES");
		c.init(1, keySpec);
		return c.doFinal(content);
	}
}