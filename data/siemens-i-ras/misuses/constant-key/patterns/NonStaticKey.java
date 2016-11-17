import javax.crypto.Cipher;

public class NonStaticKey {
	public static byte[] decrypt(byte[] key, byte[] content) {
		SecretKeySpec keySpec = new SecretKeySpec(key, "AES/EBC/PKCS5Padding");
		Cipher c = Cipher.getInstance("AES/EBC/PKCS5Padding");
		c.init(Cipher.DECRYPT_MODE, keySpec);
		return c.doFinal(content);
	}
}

public class SetEncryptMode {
	public static byte[] decrypt(byte[] content) {
		SecretKey key = getOrGenerateKey();
		Cipher c = Cipher.getInstance("AES/EBC/PKCS5Padding");
		c.init(Cipher.DECRYPT_MODE, key);
		return c.doFinal(content);
	}
	
	private static byte[] getOrGenerateKey() {
		return new byte[16];
	}
}