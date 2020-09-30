#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# A delicate script to deprecate FoodON plant and animal organisms when they
# have a subclass axiom " 'in taxon' some [NCBITaxon organism]". The subclass
# axiom is removed, and the class is converted to be about the NCBITaxon 
# organism so that all Foodon annotations and other clauses about it are kept.
# References to the existing term are switched to the new NCBITaxon term. 
# A deprecation entry is created for the existing FoodOn class.
#
# The initial run of this in Sept 2020 converted about 1782 classes.
# Its ok to re-run this - it will do the conversion on any new plant or animal
# that has an 'in taxon' link to an NCBITaxon.
#
# Classes that have 'in taxon' (x or y or z...) are left alone.
#

# see https://stackabuse.com/reading-and-writing-xml-files-in-python/
import xml.etree.ElementTree as ET

# Had to dig for this code to re-establish namespace from given XML file:
# Have to fetch existing file's dictionary of prefix:uri namespaces
namespace = dict([
    node for (_, node) in ET.iterparse('foodon-edit.owl', events=['start-ns'])
])
for prefix in namespace:
	ET.register_namespace(prefix, namespace[prefix])

tree = ET.parse('foodon-edit.owl') 
root = tree.getroot();

ns = {
	'owl':  '{http://www.w3.org/2002/07/owl#}',
	'rdfs': '{http://www.w3.org/2000/01/rdf-schema#}',
	'rdf':  '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
	'obo':  '{http://purl.obolibrary.org/obo/}'
}

count = 0;

for owl_class in root.findall('owl:Class', namespace):
	about = owl_class.attrib['{rdf}about'.format(**ns)];
	if (about and 'FOODON_' in about):
		for owl_subclassof in owl_class.findall('rdfs:subClassOf', namespace):

			for owl_restriction in owl_subclassof.findall('owl:Restriction', namespace):

				owl_property = owl_restriction.findall('owl:onProperty[@rdf:resource = "http://purl.obolibrary.org/obo/RO_0002162"]', namespace)

				if owl_property:
					owl_taxon = owl_restriction.findall('owl:someValuesFrom[@rdf:resource]', namespace);

					if owl_taxon:
						owl_taxon_uri = owl_taxon[0].attrib['{rdf}resource'.format(**ns)];
						#print ('doing', owl_taxon_uri);

						# HERE WE MAKE CHANGES
						taxon_xref = owl_class.findall('oboInOwl:hasDbXref[@rdf:resource = "'+owl_taxon_uri+'"]', namespace)
						if taxon_xref:
							#print('dbxref', about, taxon_xref[0]);
							owl_class.remove(taxon_xref[0]);
 
						label = owl_class.findall('rdfs:label[@xml:lang="en"]', namespace);
						if label:
							alt_term = owl_class.makeelement('obo:IAO_0000118', {'xml:lang': 'en'});
							alt_term.text = label[0].text;
							owl_class.append(alt_term);
							owl_class.remove(label[0]);

						# Remove existing rdf:about and add new one to class:
						owl_class.attrib.pop('{rdf}about'.format(**ns), None)
						owl_class.set('rdf:about', owl_taxon_uri);
						owl_class.remove(owl_subclassof);

						# Prepare the obsoleted FoodOn class
						obs_element = root.makeelement('owl:Class', {'rdf:about': about});

						deprecated = obs_element.makeelement('owl:deprecated', {'rdf:datatype': 'http://www.w3.org/2001/XMLSchema#boolean'});
						deprecated.text = 'true';
						obs_element.append(deprecated);

						obs_label = obs_element.makeelement('rdfs:label', {'xml:lang':'en'});
						obs_label.text = 'obsolete: ' + label[0].text;
						obs_element.append(obs_label);

						replaced = obs_element.makeelement('obo:IAO_0100001', {'rdf:resource':owl_taxon_uri});
						obs_element.append(replaced);

						root.append(obs_element);
						count += 1;

					else:
						print ("Check ", about, "for multiple taxa");

print ('processed', count , 'taxa conversions');

tree.write('foodon-edit2.owl', 
	xml_declaration=True, 
	encoding='utf-8', 
	method="xml"
)
