import javax.crypto.Cipher;

ConstructCipher {
	pattern() {
		Cipher c = Cipher.getInstance("PBEWithHmacSHA224AndAES_128");
	}
}
