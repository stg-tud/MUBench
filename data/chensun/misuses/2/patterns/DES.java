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

public class DES {
	public void encrypt(String strDataToEncrypt) {
		try {
			KeyGenerator keyGen = KeyGenerator.getInstance("DES");
			SecretKey secretKey = keyGen.generateKey();

			Cipher desCipher = Cipher.getInstance("DES/CBC/NoPadding");
			desCipher.init(Cipher.ENCRYPT_MODE,secretKey);

			byte[] byteDataToEncrypt = strDataToEncrypt.getBytes();
			byte[] byteCipherText = desCipher.doFinal(byteDataToEncrypt);
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
