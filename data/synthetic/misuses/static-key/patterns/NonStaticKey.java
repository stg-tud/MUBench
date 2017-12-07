import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

public class NonStaticKey {
	public static byte[] decrypt(byte[] key, byte[] content) throws Exception {
		SecretKeySpec keySpec = new SecretKeySpec(key, "AES");
		Cipher c = Cipher.getInstance("AES/CBC/NoPadding");
		c.init(Cipher.DECRYPT_MODE, keySpec);
		return c.doFinal(content);
	}
}
