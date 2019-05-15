import java.security.MessageDigest;

ConstructMessageDigest{
	pattern() {
		MessageDigest md = MessageDigest.getInstance("SHA-512");
	}
}
