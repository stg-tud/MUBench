import java.security.Key;
import java.security.PrivateKey;
import java.security.SecureRandom;
import javax.crypto.SecretKey;
import javax.crypto.KeyGenerator;
import android.util.Base64;

public class Encryption {
	private static byte[] decrypt(Key p3, byte[] p4) {
		if ((p3 instanceof SecretKey) == 0) {
			if ((p3 instanceof PrivateKey) != 0) {
				v0 = Cipher.getInstance("RSA/ECB/PKCS1Padding", "AndroidOpenSSL");
				v0.init(2, p3);
				v0 = v0.doFinal(p4);
			}
		} else {
			v0 = new IvParameterSpec(getCryptorIv());
			v1 = Cipher.getInstance("AES/CBC/PKCS5Padding");
			v1.init(2, p3, v0);
			v0 = v1.doFinal(p4);
		}
		return v0;
	}
	
	private static byte[] getCryptorIv() {
		v1 = com.adobe.libs.services.content.SVContext.getInstance().getAppContext().getSharedPreferences("com.adobe.libs.services.auth.SVServicesAccount.SVBlueHeronTokensCryptor", 0).getString("cloudSecretIVKey", 0);
		v0 = new byte [16];
		v0 = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
		if (v1 != 0) {
			v0 = Base64.decode(v1, 0);
		}
		return v0;
	}
	
	private static SecretKey generateRandomKey() {
		v0 = KeyGenerator.getInstance("AES");
		v1 = new SecureRandom();
		v0.init(128, v1);
		v0 = v0.generateKey();
		v2 = new byte[16];
		v1.nextBytes(v2);
		v1 = Base64.encodeToString(v2, 0);
		v2 = com.adobe.libs.services.content.SVContext.getInstance().getAppContext().getSharedPreferences("com.adobe.libs.services.auth.SVServicesAccount.SVBlueHeronTokensCryptor", 0).edit();
		v2.putString("cloudSecretIVKey", v1);
		v2.apply();
		return v0;
	}
}