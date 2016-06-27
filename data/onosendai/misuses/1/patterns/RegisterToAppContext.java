import com.vaguehope.onosendai.util.BatteryHelper;

class RegisterToAppContext {
  float pattern(Context context) {
    return BatteryHelper.level(context.getApplicationContext());
  }
}