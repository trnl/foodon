To regenerate an owl file from a robot template, run this style of command:

robot template --template wine.tsv \
  --input "../ro_import.owl" \
  --prefix "FOODON:http://purl.obolibrary.org/obo/FOODON_" \
  --prefix "RO:http://purl.obolibrary.org/obo/RO_" \
  --prefix "oboInOwl:http://www.geneontology.org/formats/oboInOwl#" \
  --prefix "schema:http://schema.org/" \
  --ontology-iri "http://purl.obolibrary.org/foodon/imports/robot_wine.owl" \
  --output ../robot_wine.owl

robot template --template pasta.tsv \
  --input "../ro_import.owl" \
  --prefix "FOODON:http://purl.obolibrary.org/obo/FOODON_" \
  --prefix "RO:http://purl.obolibrary.org/obo/RO_" \
  --prefix "oboInOwl:http://www.geneontology.org/formats/oboInOwl#" \
  --prefix "schema:http://schema.org/" \
  --ontology-iri "http://purl.obolibrary.org/foodon/imports/robot_pasta.owl" \
  --output ../robot_pasta.owl

The --input parameter is used to bring in .owl entities that are referenced in axioms
The --prefix parameter is used to expand abbreviated namespace URLs.
All output files get delivered to parent directory.  Manually import them in FoodOn (in Active Ontology -> Ontology Imports section of Protege.
