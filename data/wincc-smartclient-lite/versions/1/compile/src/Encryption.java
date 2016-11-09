import java.util.Base64;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

public class Encryption {
	byte[] encrypt(byte[] raw, byte[] clear) throws Exception {
		SecretKeySpec skeySpec = new SecretKeySpec(raw, "AES");
		Cipher cipher = Cipher.getInstance("AES");
		cipher.init(Cipher.ENCRYPT_MODE, skeySpec);
		
		byte[] encrypted = cipher.doFinal(clear);
		return encrypted;
	}

	public static String encrypt(String seed, String cleartext) throws Exception {
		byte[] rawKey = getRawKey(seed.getBytes());
		byte[] result = encrypt(rawKey, cleartext.getBytes());
		
		String fromHex = toHex(result);
		String base64 = new String(Base64.encodeToString(fromHex.getBytes(), 0));
		return base64;
	}
	
	private static byte[] getRawKey(byte[] seed) throws Exception {
		KeyGenerator kgen = KeyGenerator.getInstance("AES");
		SecureRandom sr = SecureRandom.getInstance("SHA1PRNG");
		sr.setSeed(seed);
		
		try {
			kgen.init(256, sr);
		} catch(Exception e) {
			try {
				kgen.init(192, sr);
			} catch (Exception e1) {
				kgen.init(128, sr);
			}
		}

		SecretKey skey = kgen.generateKey();
		byte[] raw = skey.getEncoded();
		return raw;
	}
	
	private static String toHex(byte[] bytes) {
		StringBuilder sb = new StringBuilder();
		for (byte b : bytes) {
			sb.append(String.format("%02X ", b));
		}
		return sb.toString();
	}
}