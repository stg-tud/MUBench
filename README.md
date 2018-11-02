<meta name="google-site-verification" content="ta5K0oMHGiDvtNp4HoHA-2-jd00GJtrq7_fW6lvTLlQ" />
<script type="application/ld+json">
{
  "@context":"http://schema.org/",
  "@type":"Dataset",
  "name":"Anam Dodhy STG TU DARMSTADT JCA",
  "description":"Testing Anam Dodhy STG TU DARMSTADT JCA",
  "url":"https://catalog.data.gov/dataset/ncdc-storm-events-database",
  "sameAs":"https://gis.ncdc.noaa.gov/geoportal/catalog/search/resource/details.page?id=gov.noaa.ncdc:C00510",
  "keywords":[
     "ATMOSPHERE > ATMOSPHERIC PHENOMENA > CYCLONES",
     "ATMOSPHERE > ATMOSPHERIC PHENOMENA > DROUGHT",
     "ATMOSPHERE > ATMOSPHERIC PHENOMENA > FOG",
     "ATMOSPHERE > ATMOSPHERIC PHENOMENA > FREEZE"
  ],
  "creator":{
     "@type":"Organization",
     "url": "https://www.ncei.noaa.gov/",
     "name":"OC/NOAA/NESDIS/NCEI > National Centers for Environmental Information, NESDIS, NOAA, U.S. Department of Commerce",
     "contactPoint":{
        "@type":"ContactPoint",
        "contactType": "customer service",
        "telephone":"+1-828-271-4800",
        "email":"ncei.orders@noaa.gov"
     }
  },
  "includedInDataCatalog":{
     "@type":"DataCatalog",
     "name":"data.gov"
  },
  "distribution":[
     {
        "@type":"DataDownload",
        "encodingFormat":"CSV",
        "contentUrl":"http://www.ncdc.noaa.gov/stormevents/ftp.jsp"
     },
     {
        "@type":"DataDownload",
        "encodingFormat":"XML",
        "contentUrl":"http://gis.ncdc.noaa.gov/all-records/catalog/search/resource/details.page?id=gov.noaa.ncdc:C00510"
     }
  ],
  "temporalCoverage":"1950-01-01/2013-12-18",
  "spatialCoverage":{
     "@type":"Place",
     "geo":{
        "@type":"GeoShape",
        "box":"18.0 -65.0 72.0 172.0"
     }
  }
}
</script>
<img align="right" width="320" height="320" alt="MUBench Logo" src="./meta/logo.png?raw=true" />

# MUBench

MUBench (pronounced "Moo Bench") is an automated benchmark for API-misuse detectors, based on [the MUBench benchmarking dataset](data).
If you encounter any problems using MUBench, please [report them to us](/stg-tud/MUBench/issues/new).
If you have any questions, please [contact Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann).

CI Status: [![CI Status](https://api.shippable.com/projects/570d22d52a8192902e1bfa79/badge?branch=master)](https://app.shippable.com/projects/570d22d52a8192902e1bfa79)

## Contributors

* [Sven Amann](http://www.stg.tu-darmstadt.de/staff/sven_amann) (Project Lead)
* [Sarah Nadi](http://www.sarahnadi.org/)
* [Hoan Anh Nguyen](https://sites.google.com/site/nguyenanhhoan/)
* [Tien N. Nguyen](http://home.eng.iastate.edu/~tien/)
* [Mattis Kämmerer](https://github.com/M8is)
* [Jonas Schlitzer](https://github.com/joschli)

## Publications

* ['*MUBench: A Benchmark for API-Misuse Detectors*'](http://sven-amann.de/publications/2016-05-MSR-MUBench-dataset.html) ([MSR '16 Data Showcase](http://2016.msrconf.org/#/data))
* ['*A Systematic Evaluation of Static API-Misuse Detectors*'](http://sven-amann.de/publications/2018-03-A-Systematic-Evalution-of-Static-API-Misuse-Detectors/) (TSE '18)

We provide [instructions to reproduce the MUBench experiments](reproduction/) presented in the above publications.

## Getting Started

With MUBench, you may run [different API-misuse detectors](detectors/) in [a number of experiments](mubench.pipeline/#experiments) to determine their precision and recall.
To this end, MUBench provides [a curated dataset of real-world projects and known misuses](data/).
In each experiment run, the respective detector emits findings which you need to review manually.
To this end, MUBench publishes (a subset of) the findings to [a review website](mubench.reviewsite/).
After you completed your reviews, the site automatically computes experiment statistics.

### Setup

1. [Setup a review (web)site](mubench.reviewsite/#setup) to publish detector findings to
2. [Setup the experiment pipeline](mubench.pipeline/#setup) to run experiments

### Use

1. [Run experiments](mubench.pipeline/#run-experiments), using `./mubench run`
2. [Publish detector findings to your review site](mubench.reviewsite/#publish-detector-findings), using `./mubench publish`

## Contribute

We want MUBench to grow, so please be welcome to

* [Add Your Own Project or Misuse to the Dataset](data/).
* [Add Your Own Detector to the Benchmark](mubench.cli/).

## License

All software provided in this repository is subject to the [CRAPL license](CRAPL-LICENSE.txt).

The detectors included in MuBench are subject to the licensing of their respective creators. See the information in [the detectors' folders](detectors).

The projects referenced in the MuBench dataset are subject to their respective licenses.

The project artwork is subject to the [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/).
