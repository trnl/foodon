#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# A script which takes in an owl rdf/xml file of deprecated terms, and searches
# in another owl rdf/xmo file for references to those terms, and replaces them 
# with the new "replaced by" (IAO:0100001) term, and saves result.
# 
# This file can be run repeatedly to keep up to date on deprecations.
#
# Command line parameters:
# argv[0]: path to deprecated terms .owl file.
# argv[1]: path of ontology file to update rdf:resource links in.


# For CRUD see https://stackabuse.com/reading-and-writing-xml-files-in-python/
import xml.etree.ElementTree as ET
import sys
from os import path

if len(sys.argv) < 2:
	sys.exit('util_obsoletion_update.py [deprecated term .owl file path] [path of ontology to update rdf:resource links in]')

deprecated_file_path = sys.argv[0];
output_file_path = 'test+' + sys.argv[1];

if not path.exists(deprecated_file_path):
	sys.exit('Unable to locate deprecated ontology term file!');

if not path.exists(sys.argv[1]):
	sys.exit('Unable to locate ontology update file!');


# Had to dig for this code to re-establish namespace from given XML file:
# Have to fetch existing file's dictionary of prefix:uri namespaces
namespace = dict([
    node for (_, node) in ET.iterparse(output_file_path, events=['start-ns'])
])
for prefix in namespace:
	ET.register_namespace(prefix, namespace[prefix]);


deprecations = ET.parse(deprecated_file_path);
deprecation_root = deprecations.getroot();

tree = ET.parse(output_file_path);
root = tree.getroot();

# For working with ElementTree attributes, it seems we need to use this format of namespace:
ns = {
	'owl':  '{http://www.w3.org/2002/07/owl#}',
	'rdfs': '{http://www.w3.org/2000/01/rdf-schema#}',
	'rdf':  '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
	'obo':  '{http://purl.obolibrary.org/obo/}'
}

count = 0;

for owl_class in deprecation_root.find('owl:Class', namespace):
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

						# "replaced by" (IAO:0100001) taxonomy term.
						replaced = obs_element.makeelement('obo:IAO_0100001', {'rdf:resource':owl_taxon_uri});
						obs_element.append(replaced);

						root.append(obs_element);
						count += 1;

					else:
						print ("Check ", about, "for multiple taxa");




tree.write(output_file_path, 
	xml_declaration=True, 
	encoding='utf-8', 
	method="xml"
)


