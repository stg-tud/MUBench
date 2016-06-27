import java.io.File;

import org.apache.jackrabbit.core.state.PMContext;

class MkDirs {
  File pattern(PMContext context) throws Exception {
    File envDir = new File(context.getHomeDir(), "db");
    if (!envDir.exists())
      envDir.mkdirs();
    return envDir;
  }
}