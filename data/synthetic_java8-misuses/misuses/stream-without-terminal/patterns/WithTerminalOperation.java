import java.util.stream.IntStream;

public class WithTerminalOperation {
    public void correctUsage() {
        IntStream.range(1, 5).forEach(System.out::println);
    }
}
