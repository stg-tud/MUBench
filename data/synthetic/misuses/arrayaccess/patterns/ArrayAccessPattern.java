public class ArrayAccessPattern {
  int pattern(int[] array, int index) {
    if (array.length < index) {
      return array[index];
    } else {
      return -1;
    }
	}
}
