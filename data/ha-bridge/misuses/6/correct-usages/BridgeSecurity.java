import javax.crypto.spec.PBEKeySpec

ConstructPBEKeySpec(password char[], salt byte[], iterationCount int, keylength int) {
	pbeks = new PBEKeySpec(password, salt, iterationCount, keylength);
}
