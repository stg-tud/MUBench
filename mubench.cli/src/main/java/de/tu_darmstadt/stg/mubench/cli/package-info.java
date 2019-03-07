/**
 * Interface to plug detectors into the MUBench Pipeline, i.e., to build MUBench runners. Runners need to be packaged as
 * an executable Jar file. This Jar's entry point should instantiate a
 * {@link de.tu_darmstadt.stg.mubench.cli.MuBenchRunner} with respective
 * {@link de.tu_darmstadt.stg.mubench.cli.DetectionStrategy}s. For an example of this, see our
 * {@link de.tu_darmstadt.stg.mubench.demo.DemoRunner}.
 */
package de.tu_darmstadt.stg.mubench.cli;
