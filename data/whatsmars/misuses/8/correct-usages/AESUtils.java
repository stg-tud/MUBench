import javax.crypto.spec.SecretKeySpec;
import javax.crypto.SecretKeyFactory;
import javax.crypto.SecretKey key;
import javax.crypto.spec.PBEKeySpec;

ConstructSecretKeySpec {
	pattern(char[] password,byte[] salt,int iterationCount,int keylength,java.lang.String algorithm) {
		SecretKeyFactory skf = SecretKeyFactory.getInstance("PBEWithHmacSHA512AndAES_128");
		PBEKeySpec pbeks = new PBEKeySpec(password, salt, iterationCount, keylength);
		SecretKey key =  skf.generateSecret(pbeks);
		byte[] keyMaterial = key.getEncoded();
		SecretKeySpec sks = new SecretKeySpec(keyMaterial, algorithm)
	}
}

