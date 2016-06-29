import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;

class SetLocale {
  String pattern(String pattern, Date date, TimeZone GMT) {
    SimpleDateFormat formatter = new SimpleDateFormat(pattern, Locale.US);
    formatter.setTimeZone(GMT);
    return formatter.format(date);
  }
}
