import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;

ConstrucCipher {
	pattern(SecureRandom random) {
		KeyGenerator kg = KeyGenerator.getInstance(AES128); 
		SecretKey key = kg.generateKey();
	        Cipher c = Cipher.getInstance("PBEWithHmacSHA224AndAES_128");
		c.init(Cipher.ENCRYPT_MODE, key, random); 	
	}
}
