import javax.crypto.spec.PBEKeySpec;

ConstructPBEKeySpec{
   pattern(char[] password, byte[] salt, int keylength) {
	PBEKeySpec pks = new PBEKeySpec(password, salt, 15000, keylength);	
   }
}
