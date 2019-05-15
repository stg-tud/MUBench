import javax.crypto.Cipher;
import java.security.SecureRandom;

ConstrucCipher {
	pattern(java.security.Key key){
	        Cipher c = Cipher.getInstance("PBEWithHmacSHA224AndAES_128");
		SecureRamdon random = SecureRandom();
		c.init(Cipher.ENCRYPT_MODE, key, random); 	
	}
}
