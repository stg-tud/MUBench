import javax.crypto.spec.PBEParameterSpec

CreateSecurePBEParameterSpec(salt java.security.SecureRandom) {
	pbeps = new PBEParameterSpec(salt, 15000);
}
