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

public class AES {
	public void encrypt(String strDataToEncrypt) {
		try {
			KeyGenerator keyGen = KeyGenerator.getInstance("AES");
			keyGen.init(128);
			SecretKey secretKey = keyGen.generateKey();

			final int AES_KEYLENGTH = 128;
			byte[] iv = new byte[AES_KEYLENGTH / 8];
			SecureRandom prng = new SecureRandom();
			prng.nextBytes(iv);

			Cipher cipher = Cipher.getInstance("AES/CBC/PKCS7Padding");

			cipher.init(Cipher.ENCRYPT_MODE, secretKey, 
					new IvParameterSpec(iv));

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

	public void decrypt(byte[] cipherText, SecretKey secretKey, byte[] iv){
		try {
			Cipher cipher = Cipher.getInstance("AES/CBC/PKCS7Padding");		
			cipher.init(Cipher.DECRYPT_MODE, secretKey, new IvParameterSpec(iv));
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
