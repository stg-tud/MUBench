import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

public class NonStaticKey {
	public static byte[] decrypt(byte[] key, byte[] content) throws Exception {
		SecretKeySpec keySpec = new SecretKeySpec(key, "AES/EBC/PKCS5Padding");
		Cipher c = Cipher.getInstance("AES/EBC/PKCS5Padding");
		c.init(Cipher.DECRYPT_MODE, keySpec);
		return c.doFinal(content);
	}
}