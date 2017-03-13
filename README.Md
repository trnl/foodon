# FOODON
[![Build Status](https://travis-ci.org/FoodOntology/foodon.svg?branch=master)](https://travis-ci.org/FoodOntology/foodon)

Our [FoodOn project home page](http://foodontology.github.io/foodon/) introduces FoodOn and its design and community.

FoodOn is initially based on a conversion of the LanguaL.org food indexing thesaurus, integrated with OBOFoundry ontology terms from UBERON, ChEBI, and NCBITaxon and others.  This approach allows  LanguaL(tm)'s thesaurus file to be updated over time, and the owl file to be updated as needed.  

Contact Us

* Join our [mailing list](https://groups.google.com/forum/#!forum/foodon-consortium/join)
* Online discussion about FoodOn terms is at the [issue tracker](https://github.com/FoodOntology/foodon/issues).
* Documentation coming soon at the [wiki page](https://github.com/FoodOntology/foodon/wiki)
* Email us at info[at]genepio.org

##To view

An easy place to browse FoodOn is at [https://www.ebi.ac.uk/ols/ontologies/foodon](https://www.ebi.ac.uk/ols/ontologies/foodon).

The foodon_core.owl main file currently contains everything FoodOn has to offer except for an indexed food product database. foodon_siren.owl has such a database included in it - over 9,000 foods from the FDA SIREN indexed food database, imported from LanguaL.org. (Currently foodon.owl is identical to foodon_core.owl).  

You can look at either file using in Protege or another OWL ontology editor.  It should import the ncbitaxon_import.owl and other imports/ files too.  Use Stanford's free [Protege](http://protege.stanford.edu) ontology editor to load the main file, and browse the Langual hierarchy under the "Classes" tab.  
