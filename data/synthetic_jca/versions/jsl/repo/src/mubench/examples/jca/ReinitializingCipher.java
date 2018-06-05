package mubench.examples.jca;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;

import java.io.BufferedReader;
import java.io.IOException;
import java.security.InvalidKeyException;
import java.security.Key;
import java.security.NoSuchAlgorithmException;
import java.util.List;

class ReinitializingCipher {
    List<byte[]> misuse(BufferedReader dataStream, Key key) throws NoSuchPaddingException, NoSuchAlgorithmException, IOException, InvalidKeyException, BadPaddingException, IllegalBlockSizeException {
        Cipher cipher = Cipher.getInstance("AES/CBC/NoPadding");
        String line;
        List<byte[]> encryptedData = new java.util.ArrayList<byte[]>();
        while ((line = dataStream.readLine()) != null) {
            cipher.init(Cipher.ENCRYPT_MODE, key);
            encryptedData.add(cipher.doFinal(line.getBytes("utf-8")));
        }
        return encryptedData;
    }
}
