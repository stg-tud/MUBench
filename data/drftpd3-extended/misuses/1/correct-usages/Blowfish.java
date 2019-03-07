import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.KeyGenerator;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.SecretKey;
import javax.crypto.spec.IvParameterSpec;

public class Blowfish {
	public void encrypt(String strDataToEncrypt) {
		try {
			KeyGenerator keyGenerator = KeyGenerator.getInstance("Blowfish");
			keyGenerator.init(128);
			SecretKey key = keyGenerator.generateKey();

			Cipher cipher = Cipher.getInstance("Blowfish/CBC/NoPadding");
			cipher.init(Cipher.ENCRYPT_MODE, key);
			
			byte[] byteDataToEncrypt = strDataToEncrypt.getBytes();
			byte[] byteCipherText = cipher.doFinal(byteDataToEncrypt);
		}

		catch (NoSuchAlgorithmException noSuchAlgo) {
		}

		catch (NoSuchPaddingException noSuchPad) {
		}

		catch (InvalidKeyException invalidKey) {
		}

		catch (BadPaddingException badPadding) {
		}

		catch (IllegalBlockSizeException illegalBlockSize) {
		}

		catch (InvalidAlgorithmParameterException invalidParam) {
		}
	}

	public void decrypt(byte[] cipherText, SecretKey secretKey){
		try {
			Cipher cipher = Cipher.getInstance("Blowfish/CBC/NoPadding");		
			cipher.init(Cipher.DECRYPT_MODE, secretKey);
			byte[] byteDecryptedText = cipher.doFinal(cipherText);
			String decryptedText = new String(byteDecryptedText);
		}

		catch (NoSuchAlgorithmException noSuchAlgo) {
		}

		catch (NoSuchPaddingException noSuchPad) {
		}

		catch (InvalidKeyException invalidKey) {
		}

		catch (BadPaddingException badPadding) {
		}

		catch (IllegalBlockSizeException illegalBlockSize) {
		}

		catch (InvalidAlgorithmParameterException invalidParam) {
		}
	}
}
