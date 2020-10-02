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
	sys.exit('Help Info:\n util_obsoletion_update.py [deprecated term .owl file path] [path of ontology to update rdf:resource links in]')

deprecated_file_path = sys.argv[1];
input_file_path = sys.argv[2];
output_file_path = sys.argv[2] + '.bak.owl';

if not path.exists(deprecated_file_path):
	sys.exit('Unable to locate deprecated ontology term file!', deprecated_file_path);

if not path.exists(input_file_path):
	sys.exit('Unable to locate ontology update file: ', input_file_path);


# Had to dig for this code to re-establish namespace from given XML file:
# Have to fetch existing file's dictionary of prefix:uri namespaces
namespace = dict([
    node for (_, node) in ET.iterparse(input_file_path, events=['start-ns'])
]);
for prefix in namespace:
	ET.register_namespace(prefix, namespace[prefix]);


deprecations = ET.parse(deprecated_file_path);
deprecation_root = deprecations.getroot();

tree = ET.parse(input_file_path);
root = tree.getroot();

print ("Using deprecated terms from:", deprecated_file_path)
print ("Updating ontology:", input_file_path)

# For working with ElementTree attributes, it seems we need to use this format of namespace:
ns = {
	'owl':  '{http://www.w3.org/2002/07/owl#}',
	'rdfs': '{http://www.w3.org/2000/01/rdf-schema#}',
	'rdf':  '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}',
	'obo':  '{http://purl.obolibrary.org/obo/}'
}

rdf_resource_lookup = {};
#rdf_resources = root.findall('.//*[@rdf:resource]', namespace);
# Look in target ontology for resource iri to replace
for tag in root.findall('.//*[@rdf:resource]', namespace): # ="'+about+'" # [@{rdf}resource]'.format(**ns), namespace

	try:
		target = tag.attrib['{rdf}resource'.format(**ns)];
		if target in rdf_resource_lookup:
			rdf_resource_lookup[target].push(tag)
		else:
			rdf_resource_lookup[target] = [tag];
		print ("adding", tag)
	except:
		continue;

count = 0;

# Look in all deprecated .owl file classes
for deprecated_cursor in deprecation_root.findall('owl:Class', namespace):
	about = deprecated_cursor.attrib['{rdf}about'.format(**ns)];

	# Find any that are mentioned to be deprecated (not bothering with boolean value).
	for owl_deprecated in deprecated_cursor.findall('owl:deprecated', namespace):
		# Term replaced by IRI
		# Note that sometimes an "X or Y ..." disjunction term can have two or
		# more replacement axioms. Not sure whats best for that case.

		owl_replacements = deprecated_cursor.findall('obo:IAO_0100001', namespace);
		if owl_replacements:
			# Some tags are 
			if owl_replacements[0].text:
				replaced_iri = owl_replacements[0].text;
			else:	
				replaced_iri = owl_replacements[0].attrib['{rdf}resource'.format(**ns)]

			#if (about == "http://purl.obolibrary.org/obo/FOODON_03412420"):
			#	print ("working on deprecation ", about, "to", replaced_iri);
			#else:
			#	continue;

			if (about in rdf_resource_lookup):
				rdf_resources = rdf_resource_lookup[about]
				# Look in target ontology for resource iri to replace
				for tag in rdf_resources:
					# Replace existing rdf:resource tag:
					tag.attrib.pop('{rdf}resource'.format(**ns), None)
					tag.set('rdf:resource', replaced_iri); # [@rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI"]
					print ('Updated', about, 'to', replaced_iri)
					count += 1;

print ('Updated', count , 'rdf:resource references.');

if (count> 0):
	tree.write(output_file_path, xml_declaration=True, encoding='utf-8', method="xml")


