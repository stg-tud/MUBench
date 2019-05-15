import javax.crypto.spec.PBEParameterSpec;
import java.security.SecureRandom;

ConstructPBEParameterSpecWithRandomizedSalt(iterationCount int) {
	salt = SecureRandom();
	pbkps = new PBEParameterSpec(salt, iterationCount);
}
