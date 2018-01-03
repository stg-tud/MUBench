import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

public class UnsynchronizedDateFormat {

	private final DateFormat format = new SimpleDateFormat("yyyyMMdd");

	public Date convert(String source) throws ParseException {
		Date d = format.parse(source);
		return d;
	}
}