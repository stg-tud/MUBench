import android.content.pm.ApplicationInfo;
import android.graphics.drawable.Drawable;

class HandleOOM {
  App pattern(ApplicationInfo appInfo) {
    App app = new App();
    app.name = (String) appInfo.loadLabel(pm);
    app.packageName = appInfo.packageName;
    
    try {
      app.icon = appInfo.loadIcon(pm);
    } catch (OutOfMemoryError e) {
      app.icon = null;
    }
    retun app;
  }
  
  class App {
  	String name;
  	String packageName;
  	Drawable icon;
  }
}