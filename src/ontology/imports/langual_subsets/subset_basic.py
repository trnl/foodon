#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**************************************************
subset_basic.py
Author: Damion Dooley
Project: FoodOn

This script generates an ontology import file based on a text file input.

INPUT
    template_import_header.txt
    [some tab delimited input file containing <import id>\t<label> ...]

OUTPUT
    [ontology_name]_import.owl

**************************************************
"""
import optparse
import sys
import os.path
import codecs
import re
import time
import requests

CODE_VERSION = '0.0.1'

def stop_err( msg, exit_code=1 ):
    sys.stderr.write("%s\n" % msg)
    sys.exit(exit_code)

class MyParser(optparse.OptionParser):
    """
    Allows formatted help info.
    """
    def format_epilog(self, formatter):
        return self.epilog


class OntoSubset(object):

    def __init__(self):

        self.ontology_name = ''
        self.subsetIdStart = None  

    def __main__(self, subsetName, subsetInputFilePath, subsetIdStart, language, prefix):
        """

        """
        self.ontology_name = subsetName
        self.subsetIdStart = subsetIdStart # Subset entries start from here

        print "Generating subset " + self.ontology_name

        owl_output_rdf = ''

        with (open(subsetInputFilePath, 'U')) as input_handle:
            for line in input_handle:
                # Lines in input are serovar id, serovar label.
                params = line.strip().split('\t')
                if len(params) == 2:
                    entity = {}
                    (importId, label) = params
                    label = label.strip()
                    code = importId.strip()
                        entity['id'] = self.get_new_subset_id(prefix)
                        entity['import_id'] = importId
                        entity['label'] = label.strip().lower()
                        entity['language'] = language

                        #DECIDE WHAT SUBCLASS ID IT SHOULD BE UNDER
                        owl_output_rdf += self.subset_entry_render(entity, subClassOfId)

        print "Saving ../" + self.ontology_name + '_import.owl'
        
        self.save_slim_owl(owl_output_rdf)


    #************************************************************

    def subset_entry_render(self, entity, subClassOfId):
        """
        """ 

        prefix = '&obo;'

        # BEGIN <owl:Class> 
        owl_output = '\n\n<owl:Class rdf:about="%s%s">\n' % (prefix, entity['id'])

        # Class hierarchy.
        owl_output += '\t<rdfs:subClassOf rdf:resource="%s%s"/>\n' % (prefix, subClassOfId)

        # Class Label
        label = entity['label'].replace('<',r'&lt;').replace('>',r'&gt;')
        labelLang = self.get_language_tag_owl(entity)

        # Definition, for now duplicating label
        title = label.split(',',1)
        title[0] = title[0].title()
        label =  ' (' + title[1].strip() +')' if len(title) > 1 else ''
        definition = ': ' + title[1].strip() if len(title) > 1 else ''
        # Some extra fancy work to make title look like [food type] ([details]) , and definition like [food type]: [details]
        owl_output += '\t<rdfs:label %(language)s>%(label)s</rdfs:label>\n' % { 'label': title[0] + label, 'language': labelLang}
        owl_output += '\t<obo:IAO_0000115 %(language)s>%(label)s</obo:IAO_0000115>\n' % { 'label': title[0] + definition, 'language': labelLang}

        # Import annotation e.g. 
        #owl_output += "\t<obo:IAO_0000412>http://langual.org</obo:IAO_0000412>\n"

        # Slim definition
        owl_output += "\t<oboInOwl:inSubset>%s</oboInOwl:inSubset>\n" % self.ontology_name

        # All subset entries are 'ready for release' IAO_0000122; Other possibility: 'requires discussion' IAO_0000428
        owl_output += '\t<obo:IAO_0000114 rdf:resource="&obo;IAO_0000122"/>\n'

        owl_output += '\t<oboInOwl:hasDbXref>%s:%s</oboInOwl:hasDbXref>\n' % (self.ontology_name.upper(), entity['import_id'] )

        owl_output += '\n</owl:Class>'
    
        return owl_output


    def get_new_subset_id(self, prefix):
        """

        """ 
        numericId = self.subsetIdStart
        self.subsetIdStart += 1
        return prefix + str(self.subsetIdStart) # + int(numericId.lstrip('0') 

    def save_slim_owl(self, owl_output_rdf):
        """
        Generate [name]_import.owl ontology file.

        """
        # DON'T CALL THIS XYZ.owl - the Makefile make reads in subdirectories and will try to parse this, and fail.
        with (open('./template_import_header.txt', 'r')) as input_handle:
            owl_template = input_handle.read()

        # SUBSTITUTE ONTOLOGY NAME
        owl_template = owl_template.replace('ONTOLOGY_NAME', self.ontology_name + '_import')
        owl_template += owl_output_rdf
        owl_template += '</rdf:RDF>'
        
        with (codecs.open('./' + self.ontology_name + '_import.owl', 'w', 'utf-8')) as output_handle:
            output_handle.write(owl_template)


    def get_language_tag(self, entity):
        if 'language' in entity:
            return '@' + entity['language']
        else:
            return ''


    def get_language_tag_owl(self, entity):
        if 'language' in entity:
            return 'xml:lang="' + entity['language'] + '"'
        else:
            return ''

if __name__ == '__main__':


    # Generates Subset for given input file.
    subset = OntoSubset()
    # Provide name, input lookup table, starting id, and language of content:
    # NOTE: no leading 0's allowed at moment. FUTURE FIX.
    subset.__main__('subset_salmonella', './salmonella.txt', 1000010, 'en', 'GENEPIO_') 

    



