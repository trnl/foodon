---
layout: ontology_detail
id: foodon
title: foodon
jobs:
  - id: https://travis-ci.org/FoodOntology/foodon
    type: travis-ci
build:
  checkout: git clone https://github.com/FoodOntology/foodon.git
  system: git
  path: "."
contact:
  email: cjmungall@lbl.gov
  label: Chris Mungall
description: foodon is an ontology...
domain: stuff
homepage: https://github.com/FoodOntology/foodon
products:
  - id: foodon.owl
  - id: foodon.obo
dependencies:
 - id: bfo
 - id: ro
 - id: envo
 - id: uberon
 - id: chebi
tracker: https://github.com/FoodOntology/foodon/issues
license:
  url: http://creativecommons.org/licenses/by/3.0/
  label: CC-BY
---

Enter a detailed description of your ontology here
