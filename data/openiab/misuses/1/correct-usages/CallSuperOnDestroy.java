import com.unity3d.player.UnityPlayerActivity;

class CallSuperOnDestroy extends UnityPlayerActivity {
  @Override
  protected void onDestroy() {
    super.onDestroy();
    // do other cleanup...
  }
}