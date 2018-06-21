# Findbugs

The Findbugs runner requires a [filter file](http://findbugs.sourceforge.net/manual/filter.html) that configures the Findbugs analyses to run.
You can use any file in [configs/](configs/) or create your own file and invoke the detector with

    --java-options Dfindbugs.config=/mubench/detectors/Findbugs/configs/<filter-file-name>.xml

The runner provides the [Findbugs core bug patterns](http://findbugs.sourceforge.net/bugDescriptions.html), as well as the [FindSecBugs bug patterns](http://find-sec-bugs.github.io/bugs.htm).
