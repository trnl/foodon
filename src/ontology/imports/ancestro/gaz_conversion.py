#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
gaz_conversion.py
Author: Damion Dooley
Project: FoodOn

The EBI Ancestry Ontology ancestro is great but it doesn't use
gazetteer ids.  This script replaces ancestro geo ids with gazetteer 
ones according to the ancestro_gaz_conversion.txt lookup table.
For swapped records, converts e.g. '<rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">Macanese</rdfs:label>' to an alternate label.

The ancestro_import.owl.txt file is a version of ancestro.owl 
stripped of anything the food ontology doesn't need, namely
"ancestry status", and "obsolete class"

The reason ancestro_import.owl.txt is named the way it is is 
that protege tends to go searching for .owl files, and can 
accidentally link up the wrong ancestro_import.owl file; 
so we put .txt at end to stop it from doing that.

INPUT:
	ancestro_import.owl.txt
	ancestro_gaz_conversion.txt

OUTPUT:
	../ancestro_import.owl
"""


with open('./ancestro_import.owl.txt', 'r') as handle:
    ontology = handle.read()

# Perform search and replace on all Ancestro geo ids to Gazetteer ids:
with open('./ancestro_gaz_conversion.txt', 'r') as handle:
	for line in handle:
		(search, replace) = line.strip().split('\t') #tab delimited
		searchURI = 'http://www.ebi.ac.uk/ancestro/' + search
		replaceURI = 'http://purl.obolibrary.org/obo/' + replace 
		ontology = ontology.replace( searchURI + '"', replaceURI + '"')

		# Now make an alternate label IAO_00001118 out of all GAZ class rdfs:label tags.
		# <rdfs:label rdf:datatype="http://www.w3.org/2001/XMLSchema#string">South-Eastern Asia</rdfs:label>
		startClass = ontology.find('<owl:Class rdf:about="' + replaceURI)
		#ontology = ontology[0:startClass] + ontology[startClass:].replace('rdfs:label','obo:IAO_0000118',2)
		endClass = ontology.find('</owl:Class>', startClass)

		# OR ELIMINATE All Ancestro labels, since they will be replaced with Gaz labels
		startLabel = ontology.find('<rdfs:label', startClass)
		if startLabel < endClass:
			endLabel = ontology.find('</rdfs:label>', startLabel) + 13
			ontology = ontology[0:startLabel] + ontology[endLabel:]

with open('../ancestro_import.owl', 'w') as handle:
    handle.write(ontology)