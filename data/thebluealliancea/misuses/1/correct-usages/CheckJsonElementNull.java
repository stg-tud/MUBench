import com.google.gson.JsonElement;

class CheckJsonElementNull {
  String pattern(JsonElement d) {
    if (!d.isJsonNull())
      return d.getAsString();
    else
      return ""; // some default
  }
}
