import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Date;

public class UnsynchronizedDateFormatCorrected {

	private final DateFormat format = new SimpleDateFormat("yyyyMMdd");
	 
	public Date convert(String source) throws ParseException {
		synchronized (format) {
			Date d = format.parse(source);
			return d;
		}
	}

}
