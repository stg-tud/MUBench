# A Systematic Evaluation of Static API-Misuse Detectors

* Published in: TSE'18 ([details](http://sven-amann.de/publications/2018-03-A-Systematic-Evalution-of-Static-API-Misuse-Detectors/))
* Review site: http://www.st.informatik.tu-darmstadt.de/artifacts/mubench/reviews/tse17/

To reproduce MUBench experiments, please first read our [Getting Started guide](../../../#getting-started).
Once you've setup the experiment pipeline, you may rerun experiments by executing the respective commands listed below.
Afterwards, you may publish the detector findings to a review site for manual assessment.

## Experiment P (Precision)

    mubench> pipeline run ex2 DMMC --tag TSE17 --datasets TSE17-ExPrecision --timeout 7200 --java-options Xmx16G
    mubench> pipeline run ex2 GrouMiner --tag TSE17 --datasets TSE17-ExPrecision --timeout 7200 --java-options Xmx16G
    mubench> pipeline run ex2 Jadet --tag TSE17 --datasets TSE17-ExPrecision --timeout 7200 --java-options Xmx16G Dorg.softevo.oumextractor.javajarsdirs=/opt/jdk/jre/lib
    mubench> pipeline run ex2 Tikanga --tag TSE17 --datasets TSE17-ExPrecision --timeout 7200 --java-options Xmx16G Dorg.softevo.oumextractor.javajarsdirs=/opt/jdk/jre/lib

## Experiment RUB (Recall Upper Bound)

    mubench> pipeline run ex1 DMMC --tag TSE17 --datasets TSE17-ExRecallUpperBound --java-options Xmx16G
    mubench> pipeline run ex1 GrouMiner --tag TSE17 --datasets TSE17-ExRecallUpperBound --java-options Xmx16G
    mubench> pipeline run ex1 Jadet --tag TSE17 --datasets TSE17-ExRecallUpperBound --java-options Xmx16G Dorg.softevo.oumextractor.javajarsdirs=/opt/jdk/jre/lib
    mubench> pipeline run ex1 Tikanga --tag TSE17 --datasets TSE17-ExRecallUpperBound --java-options Xmx16G Dorg.softevo.oumextractor.javajarsdirs=/opt/jdk/jre/lib

## Experiment R (Recall)

    mubench> pipeline run ex3 DMMC --tag TSE17 --datasets TSE17-ExRecall TSE17-ExPrecision-TruePositives --timeout 7200 --java-options Xmx16G
    mubench> pipeline run ex3 GrouMiner --tag TSE17 --datasets TSE17-ExRecall TSE17-ExPrecision-TruePositives --timeout 7200 --java-options Xmx16G
    mubench> pipeline run ex3 Jadet --tag TSE17 --datasets TSE17-ExRecall TSE17-ExPrecision-TruePositives --timeout 7200 --java-options Xmx16G Dorg.softevo.oumextractor.javajarsdirs=/opt/jdk/jre/lib
    mubench> pipeline run ex3 Tikanga --tag TSE17 --datasets TSE17-ExRecall TSE17-ExPrecision-TruePositives --timeout 7200 --java-options Xmx16G Dorg.softevo.oumextractor.javajarsdirs=/opt/jdk/jre/lib
