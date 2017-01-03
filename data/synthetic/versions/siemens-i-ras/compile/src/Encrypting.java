import javax.crypto.spec.SecretKeySpec;
import javax.crypto.Cipher;

public class Encrypting {
	public static byte[] encryptWithKey(byte[] content) throws Exception {
		// using a constant key is unsafe
		SecretKeySpec keySpec = new SecretKeySpec("RAS".getBytes("UTF-8"), "AES/CBC/PKCS5Padding");
		Cipher c = Cipher.getInstance("AES");
		c.init(Cipher.ENCRYPT_MODE, keySpec);
		return c.doFinal(content);
	}
	
	private static byte[] encrypt(byte[] key, byte[] content) throws Exception {
		// "AES" has an unsafe default configuration of "AES/EBC/PKCS5Padding"
		SecretKeySpec keySpec = new SecretKeySpec(key, "AES");
		Cipher c = Cipher.getInstance("AES");
		c.init(Cipher.ENCRYPT_MODE, keySpec);
		return c.doFinal(content);
	}
}