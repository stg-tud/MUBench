import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import static com.orangelabs.rcs.utils.StringUtils.UTF8;

class HashWithExplicitEncoding {
  byte[] pattern(String callId, byte[] secretKey) {
    SecretKeySpec sks = new SecretKeySpec(secretKey, "HmacSHA1");
    Mac mac = Mac.getInstance("HmacSHA1");
    mac.init(sks);
    return mac.doFinal(callId.getBytes(UTF8));
  }
}