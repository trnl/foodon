#!/usr/bin/python
# -*- coding: utf-8 -*-

""" 
**************************************************
conversion.py
Author: Damion Dooley

This script generates SLIM files for indexed Langual food databases.
An issue is that often the 3rd party databases have their own ID scheme.
To reuse LanguaL updates we would need to translate existing db food term ids
over to persistent LanguaL ids.  This works for a few databases of [alpha][digits] format.

The script loads the database.json and langual_facet_a.json database in order
to map each indexed food term over into an equivalency conjunction logic statement.

Subsets are outputted to the current directory.  To utilize them in a FoodOn install,
move them up a level and import them into your instance of FoodOn via Protege or manually
by editing the top of foodon-edit.owl or foodon.owl 

INPUT
    ./template_import_header.txt
    ../langual/database.json
    ../langual/langual_facet_a.json
    ./[ontology name].TXT # A tab-delimited data file

OUTPUT
    ./[ontology name]_import.owl.txt

    Output has .txt on end to ensure that Protege doesn't reference it.  
    All references should just be to files in the /imports folder directly,
    so if using it, move output file up to /imports and rename.

**************************************************
"""
import json
import optparse
import sys
import os.path
import codecs
import re
import time
import requests

try: #Python 2.7
    from collections import OrderedDict
except ImportError: # Python 2.6
    from ordereddict import OrderedDict

#FOR LOADING JSON AND PRESERVING ORDERED DICT SORTING. 
try:    
    import simplejson as json
except ImportError: # Python 2.6
    import json


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


class Langual(object):

    def __init__(self):

        # READ THIS FROM database.json
        self.database = {} 
        self.database_path = '../langual/database.json' 
        self.product_type_path = '../langual/langual_facet_a.json'
        self.ontology_name = ''
        self.subsetIdStart = None  
        self.counts = {}
        self.label_reverse_lookup = {}

        self.get_database_JSON()


    def __main__(self, subsetName, subsetInputFilePath, subsetIdStart, language):
        """

        """
        self.ontology_name = subsetName
        self.subsetIdStart = subsetIdStart # Slim entries start from here

        print "Generating subset " + self.ontology_name

        owl_output_rdf = ''

        with (open(subsetInputFilePath, 'U')) as input_handle:
            for line in input_handle:
                # Lines in input are :Database native id[tab]label[tab]LanguaL ids.
                params = line.strip().split('\t')
                if len(params) == 4 and params[0] != 'FOODID':
                    entity = {}
                    (importId, label, altLabel, langualCodes) = params
                    label = label.strip()
                    altLabel = altLabel.strip()
                    langualCodes = langualCodes.strip()
                    if (len(importId)>0 and len(label)>0 and len(langualCodes)>0):
                        entity['import_id'] = importId
                        entity['label'] = label.strip().lower()
                        entity['langual_ids'] = langualCodes.split()
                        # Translates ids to FoodOn id range.
                        entity['id'] = self.get_new_subset_id(importId) 
                        entity['language'] = language
                        owl_output_rdf += self.subset_entry_render(entity)

        print "Saving ../" + self.ontology_name + '_import.owl'
        
        self.save_subset_owl(owl_output_rdf)


    #************************************************************

    def subset_entry_render(self, entity):
        """
        Enhance entity with LanguaL facet-specific attributes.  Facet letters D,I,L,O don't exist in LanguaL.
        """ 

        prefix = '&obo;'

        facet_relations_rdf = ''
        subClassOfId = None

        for langual_id in entity['langual_ids']:

            # Lookup existing LanguaL entity if any.
            if not (langual_id in self.database['index']):
                print 'Unable to find id "' + langual_id + '" in LanguaL database.'
                continue

            refEntity = self.database['index'][langual_id]
            # We skip doing references to "ignore" items
            if refEntity['status'] == 'ignore': 
                continue

            # If item is depreciated, then if it is a [food item]_added, and the [food item] exists
            # If so, change refEntity to that item
            label = refEntity['label']['value'].lower()
            if refEntity['status'] == 'deprecated':
                if refEntity['database_id'][0] == 'H' and label[-6:] == ' added' and label[0:-6] in self.label_reverse_lookup:
                    print "Replaced secondary ingredient with "
                    refEntity = self.label_reverse_lookup[ label[0:-6] ]
                # These are junky parts of conjunction
                elif label[0:3] == 'no ' or label[-10:] == ' not known' or label[-14:] == 'not applicable': 
                    continue

            # Stats on count of members of each LanguaL facet, which is first letter of entity id.
            category = langual_id[0]
            if category in self.counts: 
                self.counts[category] += 1 
            else: 
                self.counts[category] = 1

            # To do OWL links we have to refer to the entity's ontology id.
            ontology_id = refEntity['ontology_id'] 
            relation = None

            # A. PRODUCT TYPE [A0361]
            # A particular database/subset may reference only one Product Type Hierarchy, e.g. an US FDA one.
            # This is handled separately as rdfs:subClassOf
            if category == 'A': subClassOfId = ontology_id # 'rdfs:subClassOf'   

            # B. FOOD SOURCE [B1564]
            # This is always the primary ingredient, attached using the 'has primary substance added'
            # - Includes raw animal, plant, bacteria and fungi ingredients.
            if category == 'B': relation = '&obo;FOODON_00001563' # Has primary substance added'.  Awaiting RO relation

            # C. PART OF PLANT OR ANIMAL [C0116]
            elif category == 'C': relation = '&obo;RO_0001000' # Part Of

            # E. PHYSICAL STATE, SHAPE OR FORM [E0113]
            elif category == 'E': relation = '&obo;RO_0000086' # Has Quality

            # F. EXTENT OF HEAT TREATMENT [F0011]
            elif category == 'F': relation = '&obo;RO_0000086' # Has Quality

            # G. COOKING METHOD [G0002]
            elif category == 'G': relation = '&obo;RO_0002354' # formed as a result of

            #H. TREATMENT APPLIED [H0111]
            elif category == 'H': 
                if label[-6:] == ' added':
                    # Exception: if word " added" at end, then "has substance added"  and keep deprecated reference in order to address this later.
                    relation = '&obo;FOODON_00001560' # "has substance added"
                else:
                    relation = '&obo;RO_0002354' # formed as a result of
            

            #J. PRESERVATION METHOD [J0107]
            elif category == 'J': relation = '&obo;RO_0002354' # formed as a result of

            #K. PACKING MEDIUM [K0020]
            elif category == 'K' and langual_id != 'K0003': 
                relation = '&obo;FOODON_00001301' # Immersed in.  Awaiting RO relation.  RO_0001025 Located In (preferrably "immersed in")

            #M. CONTAINER OR WRAPPING [M0100]
            elif category == 'M': relation = '&obo;PATO_0005016' # surrounded by / RO_0002002 has 2D boundary 

            #N. FOOD CONTACT SURFACE [N0010]
            elif category == 'N': relation = '&obo;RO_0002220' # Adjacent to (AT SOME POINT IN TIME)

            #P. CONSUMER GROUP/DIETARY USE/LABEL CLAIM [P0032]
            elif category == 'P': relation = '&obo;FOODON_00001302' # Has Consumer / RO_0000086 has Quality

            #R. GEOGRAPHIC PLACES AND REGIONS [R0010]
            elif category == 'R': relation = 'http://www.ebi.ac.uk/ancestro/ancestro_0308' # Has country of origin

            #Z. ADJUNCT CHARACTERISTICS OF FOOD [Z0005]
            elif category == 'Z': relation = '&obo;RO_0000086' # Has Quality
            
            if relation:
                facet_relations_rdf += '''
                        <owl:Restriction>
                            <owl:onProperty rdf:resource="%s"/>
                            <owl:someValuesFrom rdf:resource="&obo;%s"/>
                        </owl:Restriction>
            ''' % (relation, ontology_id)

        # BEGIN <owl:Class> 
        owl_output = '\n\n<owl:Class rdf:about="%s%s">\n' % (prefix, entity['id'])

        # Product type is used for class hierarchy.
        if subClassOfId:
            owl_output += '\t<rdfs:subClassOf rdf:resource="%s%s"/>\n' % (prefix, subClassOfId)

        # Class Label
        label = entity['label'].replace('<',r'&lt;').replace('>',r'&gt;')
        labelLang = self.get_language_tag_owl(entity)

        # Definition, for now duplicating label
        title = label.split(',',1)
        title[0] = title[0].lower() # .title()

        label = ''
        definition = ''
        if len(title) > 1:
            label = ' (' + title[1].strip() +')' 
            definition = ': ' + title[1].strip()
        # All langual indexed foods are food products.  Stating this here to make it distinct from 
        # food source items that may have same name.
        elif 'en' in entity['language'] and not 'product' in title[0]:
            title[0] = title[0] + ' (food product)'

        # Some extra fancy work to make title look like [food type] ([details]) , and definition like [food type]: [details]
        owl_output += '\t<rdfs:label %(language)s>%(label)s</rdfs:label>\n' % { 'label': title[0] + label, 'language': labelLang}
        owl_output += '\t<obo:IAO_0000115 %(language)s>%(label)s</obo:IAO_0000115>\n' % { 'label': title[0] + definition, 'language': labelLang}

        # LanguaL import annotation
        owl_output += "\t<obo:IAO_0000412>http://langual.org</obo:IAO_0000412>\n"

        # Slim definition
        owl_output += "\t<oboInOwl:inSubset>%s</oboInOwl:inSubset>\n" % self.ontology_name

        # All Slim entries are 'ready for release' IAO_0000122
        # Other possibility: 'requires discussion' IAO_0000428
        owl_output += '\t<obo:IAO_0000114 rdf:resource="&obo;IAO_0000428"/>\n'

        owl_output += '\t<oboInOwl:hasDbXref>%s:%s</oboInOwl:hasDbXref>\n' % (self.ontology_name.upper(), entity['import_id'] )

        if len(facet_relations_rdf):
            #  <rdf:Description rdf:about="&obo;%s"/>
            owl_output += '''
    <owl:equivalentClass>
        <owl:Class>
            <owl:intersectionOf rdf:parseType="Collection">
                %s
            </owl:intersectionOf>
        </owl:Class>
    </owl:equivalentClass>
            ''' % (facet_relations_rdf)  #entity['id'], 

        owl_output += '\n</owl:Class>'
    
        return owl_output


    def get_new_subset_id(self, id):
        """
        SLIM item id is mapped over to FOODON_ namespace such that subsequent 
        loads of the SLIM items preserve same ids.
        """ 
        numericId = ''.join(i for i in id if i.isdigit()).lstrip('0') # may contain leading 0's
        return 'FOODON_' + format(self.subsetIdStart + int(numericId), '08' ) # padded with 0 to 8 digits


    def save_subset_owl(self, owl_output_rdf):
        """
        Generate [subset]_import.owl ontology file.

        """
        # DON'T CALL THIS XYZ.owl - the Makefile make reads in subdirectories and will try to parse this, and fail.
        with (open('./template_import_header.txt', 'r')) as input_handle:
            owl_template = input_handle.read()

        # SUBSTITUTE ONTOLOGY NAME
        owl_template = owl_template.replace('ONTOLOGY_NAME', self.ontology_name + '_import')
        owl_template += owl_output_rdf 
        owl_template += '</rdf:RDF>'
        
        with (codecs.open('./' + self.ontology_name + '_import.owl.txt', 'w', 'utf-8')) as output_handle:
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


    def get_database_JSON(self):
        """
        Load existing JSON representation of import database (created last time OWL ontology was saved)
        Will be updated if database has changed.
        """

        with open(self.database_path) as data_file:    
            dbObject = json.load(data_file, object_pairs_hook=OrderedDict) 

        with open(self.product_type_path) as data_file:
            dbObject2 = json.load(data_file, object_pairs_hook=OrderedDict)
        
        for item in dbObject2['index']:
            dbObject['index'][item] = dbObject2['index'][item]

        self.database = dbObject

        # Create a reverse-lookup index by food source label, or extract, concentrate etc.
        for item in dbObject['index']:
            # C0228 == extract, concentrate or isolate of plant or animal
            if item[0] == 'B' or self.itemAncestor(item, ['C0228']): 
                entity = dbObject['index'][item]
                if not (entity['status'] == 'deprecated' or entity['status'] == 'ignore'):
                    self.label_reverse_lookup[entity['label']['value'].lower()] = entity


    def itemAncestor(self, item, ancestors):
        # Determine if item has ancestor in ancestors array.
        stack = [item]
        tried = []
        while len(stack):
            langualID = stack.pop(0)
            tried.append(langualID)
            if langualID in self.database['index']:
                for parent in self.database['index'][langualID]['is_a']:
                    entity = self.database['index'][langualID]['is_a'][parent]
                    parentId = entity['value']
                    if parentId in ancestors:
                        return True
                    elif parentId in self.database['index'] and parentId not in tried:
                        stack.append(parentId) 
        return False


if __name__ == '__main__':


    # Generates Slim for given input file.
    foodstruct = Langual()
    # See http://www.langual.org/langual_indexed_datasets.asp for list of indexed food databases
    # A version of the SIREN food index has been done and moved to imports folder
    foodstruct.__main__('subset_siren', './DBFSIREN.TXT', 3300000, 'en') #F1000 - F17788 

    # Main LanguaL import facet terms occupy FoodOn ids in range 3,400,000 -> 3,420,000

    foodstruct.__main__('subset_caroteno', './CAROTENO.TXT', 3444000, 'en') # CR0010 - CR4162
    foodstruct.__main__('subset_usda_sr8', './USDA Standard Reference 8.TXT', 3450000, 'en') # 1001 - 21140
    foodstruct.__main__('subset_french', './FRENCH.TXT', 3500000, 'fr') # FR03010 - FR51572 (RECORD FR99999 REMOVED)

    # NOT DONE YET... id mapping issue.
    #foodstruct.__main__('subset_who', './WHO.TXT', 3300000, 'en') # ISSUE: some numeric ID's end in "A" to avoid duplicates
    #foodstruct.__main__('subset_codex', './CODEX.TXT', 3300000, 'en') # CX[A-163]-[...]




