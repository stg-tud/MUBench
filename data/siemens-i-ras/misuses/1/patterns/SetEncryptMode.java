import javax.crypto.Cipher;

public class SetEncryptMode {
	public void useSafeAESInstance()
	{
		Cipher.getInstance("AES/CBC/PKCS5Padding");
	}
}