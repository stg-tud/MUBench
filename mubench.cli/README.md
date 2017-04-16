<img align="right" width="320" height="320" alt="MUBench Logo" src="https://raw.githubusercontent.com/stg-tud/MUBench/master/meta/logo.png" />

# MUBench : Benchmarking

If you have a detector set up for running on MUBench, please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) to have it added to the benchmark.

### Benchmark Your Own Detector

For MUBench to run your detector and interpret its results, your detector's executable needs to comply with MUBench's command-line interface. The easiest way to achieve this is for your entry-point class to extend `MuBenchRunner`, which comes with the Maven dependency [`de.tu-darmstadt.stg:mubench.cli`](https://github.com/stg-tud/MUBench/tree/master/mubench.cli) via our repository at `http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/mvn/`.

A typical MUBench Runner looks like this:

    public class XYRunner extends MuBenchRunner {
      public static void main(String[] args) {
        new XYRunner().run(args);
      }
      
      void detectOnly(CodePath patternPath, CodePath targetPath, DetectorOutput output) throws Exception {
        ...
      }
      
      void mineAndDetect(CodePath trainingAndTargetPath, DetectorOutput output) throws Exception {
        ...
      }
    }

Currently, Runners should support two run modes:

1. "Detect Only"-mode, where the detector is provided with hand-crafted patterns (a one-method class implementing the correct usage) and some target code to find violations of these patterns in. All input is provided as Java source code and corresponding Bytecode.
2. "Mine and Detect"-mode, where the detector should mine its own patterns in the provided code base and find violations in that same code base. Again, input is provided as source code and corresponding Bytecode.

The `DetectorOutput` is essentially a collection where you add your detector's findings. MUBench expects you to add the findings ordered by the detector's confidence, descending.

To register your own detector to MUBench, the following steps are necessary:

1. Create a new subfolder `my-detector` in the [detectors](https://github.com/stg-tud/MUBench/tree/master/detectors) folder. `my-detector` will be the Id used to refer to your detector when running experiments.
2. Add the executable JAR with your detector as `my-detector/my-detector.jar`.
3. Run MUBench as usual.

## License

All software provided in this repository is subject to the [CRAPL license](https://github.com/stg-tud/MUBench/tree/master/CRAPL-LICENSE.txt).

The detectors included in MuBench are subject to the licensing of their respective creators. See the information in [the detectors' folders](https://github.com/stg-tud/MUBench/tree/master/detectors).

The projects referenced in the MuBench dataset are subject to their respective licenses.

The project artwork is subject to the [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
