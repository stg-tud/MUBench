import java.sql.ResultSet;
import java.sql.SQLException;

import org.hibernate.HibernateException;

import org.joda.time.DateTime;
import org.joda.time.Interval;
import org.joda.time.contrib.hibernate.PersistentDateTime;

class CheckStartDateForNull {
  Object nullSafeGet(ResultSet resultSet, String[] names) throws HibernateException, SQLException {
    if (resultSet == null)
    {
      return null;
    }
    PersistentDateTime pst = new PersistentDateTime();
    DateTime start = (DateTime) pst.nullSafeGet(resultSet, names[0]);
    DateTime end = (DateTime) pst.nullSafeGet(resultSet, names[1]);
    if (start == null || end == null) {
        return null;
    }
    return new Interval(start, end);
  }
}