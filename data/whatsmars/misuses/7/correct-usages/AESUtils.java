package org.hongxi.whatsmars.common.util;

import org.apache.commons.codec.binary.Base64;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.DESKeySpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;


public class DESUtils {
    private static final String DES = "AES"; //DES before
    private static final String PADDING = "AES/CBC/PKCS5Padding"; // "DES/ECB/PKCS5Padding" was being used before and is insecure
    private static final String DEFAULT_ENCODING = "utf-8";

    public final static String encrypt(String code, String key) {
        try {
            return Base64.encodeBase64String(encrypt(code.getBytes(DEFAULT_ENCODING), key
                    .getBytes(DEFAULT_ENCODING)));
        } catch (Exception e) {
            //
        }
        return null;

    }

    public static byte[] encrypt(byte[] src, byte[] key) throws Exception {
        /*
        SecureRandom sr = new SecureRandom();
        DESKeySpec dks = new DESKeySpec(key);
        SecretKeyFactory keyFactory = SecretKeyFactory.getInstance(DES);
        SecretKey securekey = keyFactory.generateSecret(dks);
        */

        //randomization of the key
        SecureRandom secRandom = new SecureRandom();
        secRandom.nextBytes(key);
        SecretKeySpec secretKey = new SecretKeySpec(key, DES);

        Cipher cipher = Cipher.getInstance(PADDING);
        cipher.init(Cipher.ENCRYPT_MODE, secretKey);
        return cipher.doFinal(src);

    }

    public final static String decrypt(String data, String key) {
        try {
            //base64,default-charset is UTF-8
            return new String(decrypt(Base64.decodeBase64(data),
                    key.getBytes(DEFAULT_ENCODING)), DEFAULT_ENCODING);

        } catch (Exception e) {
            //
        }
        return null;
    }

    public static byte[] decrypt(byte[] src, byte[] key) throws Exception {
        /*
        SecureRandom sr = new SecureRandom();
        DESKeySpec dks = new DESKeySpec(key);
        SecretKeyFactory keyFactory = SecretKeyFactory.getInstance(DES);
        SecretKey securekey = keyFactory.generateSecret(dks);
        */

        //randomization of the key
        SecureRandom secRandom = new SecureRandom();
        secRandom.nextBytes(key);
        SecretKeySpec secretKey = new SecretKeySpec(key, DES);

        Cipher cipher = Cipher.getInstance(PADDING);
        cipher.init(Cipher.DECRYPT_MODE, secretKey);
        return cipher.doFinal(src);
    }


}