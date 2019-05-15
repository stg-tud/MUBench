import javax.crypto.spec.IvParameterSpec;
import java.security.SecureRandom;

ConstructIvParameterSpec {
	pattern() {
		SecureRandom iv = SecureRandom(); 
		IvParameterSpec ips = new IvParameterSpec(iv);
	}
}
