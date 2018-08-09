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
import java.security.MessageDigest;

public class AES {
	public void encrypt(String strDataToEncrypt) {
		try {
			MessageDigest messageDigest = null;

            messageDigest = MessageDigest.getInstance("MD5");
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
			Cipher aesCipherForDecryption = Cipher.getInstance("AES/CBC/PKCS7Padding");
			aesCipherForDecryption.init(Cipher.DECRYPT_MODE, secretKey, new IvParameterSpec(iv));
			byte[] byteDecryptedText = aesCipherForDecryption.doFinal(cipherText);
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
