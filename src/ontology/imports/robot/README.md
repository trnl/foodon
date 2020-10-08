To regenerate an owl file from a robot template, run this style of command:
NOTE: --input command ONLY ALLOWS ONE INPUT file; if you do multiple --input
only LAST one is used.

robot template --template wine.tsv \
  --input "../ro_import.owl" \
  --prefix "FOODON:http://purl.obolibrary.org/obo/FOODON_" \
  --prefix "RO:http://purl.obolibrary.org/obo/RO_" \
  --prefix "oboInOwl:http://www.geneontology.org/formats/oboInOwl#" \
  --prefix "schema:http://schema.org/" \
  --ontology-iri "http://purl.obolibrary.org/obo/foodon/imports/robot_wine.owl" \
  --output ../robot_wine.owl

robot template --template pasta.tsv \
  --input "../ro_import.owl" \
  --prefix "FOODON:http://purl.obolibrary.org/obo/FOODON_" \
  --prefix "RO:http://purl.obolibrary.org/obo/RO_" \
  --prefix "oboInOwl:http://www.geneontology.org/formats/oboInOwl#" \
  --prefix "schema:http://schema.org/" \
  --ontology-iri "http://purl.obolibrary.org/obo/foodon/imports/robot_pasta.owl" \
  --output ../robot_pasta.owl

robot template --template fdc.tsv \
  --input "../ro_import.owl" \
  --prefix "FOODON:http://purl.obolibrary.org/obo/FOODON_" \
  --prefix "IAO:http://purl.obolibrary.org/obo/IAO_" \
  --prefix "RO:http://purl.obolibrary.org/obo/RO_" \
  --prefix "oboInOwl:http://www.geneontology.org/formats/oboInOwl#" \
  --prefix "schema:http://schema.org/" \
  --prefix "rdfs:http://www.w3.org/2000/01/rdf-schema#" \
  --ontology-iri "http://purl.obolibrary.org/obo/foodon/imports/robot_fdc.owl" \
  --output ../robot_fdc.owl

robot template --template organismal_materials.tsv \
  --input "../../foodon-merged.owl" \
  --prefix "PO:http://purl.obolibrary.org/obo/PO_" \
  --prefix "FOODON:http://purl.obolibrary.org/obo/FOODON_" \
  --prefix "IAO:http://purl.obolibrary.org/obo/IAO_" \
  --prefix "RO:http://purl.obolibrary.org/obo/RO_" \
  --prefix "oboInOwl:http://www.geneontology.org/formats/oboInOwl#" \
  --prefix "schema:http://schema.org/" \
  --prefix "rdfs:http://www.w3.org/2000/01/rdf-schema#" \
  --ontology-iri "http://purl.obolibrary.org/obo/foodon/imports/robot_organismal_materials.owl" \
  --output ../robot_organismal_materials.owl

The --input parameter is used to bring in .owl entities that are referenced in axioms
The --prefix parameter is used to expand abbreviated namespace URLs.
All output files get delivered to parent directory.  Manually import them in FoodOn (in Active Ontology -> Ontology Imports section of Protege.
