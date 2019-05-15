import javax.crypto.spec.IvParameterSpec;
import java.security.SecureRandom;

ConstructRandomizedIV(offset int, len int) {
	random = SecureRandom();
	iv = new IvParameterSpec(random);
}
