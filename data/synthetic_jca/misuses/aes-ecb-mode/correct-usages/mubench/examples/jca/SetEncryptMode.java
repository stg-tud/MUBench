package mubench.examples.jca;

import javax.crypto.Cipher;

public class SetEncryptMode {
	public void useSafeAESInstance() throws Exception {
		Cipher.getInstance("AES/CBC/NoPadding");
	}
}
