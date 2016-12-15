#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Script that converts an Adlib XML (Taxonomy) into VDEX 
    Andre Goncalves <andre@intk.com>
"""

from lxml import etree
from imsvdex.vdex import VDEXManager
from pkg_resources import resource_stream
import datetime

XML_PATH = "Taxonomies-v02.xml"
EXPORT_FILE_PATH = "taxonomies-%s.vdex"


class XMLtoVDEX:
    def __init__(self, vocabulary_name, vocabulary_identifier):
        self.records = []
        self.vdex_file = None
        self.vdexmanager = None
        self.file_name = None
        self.vocabulary_name = vocabulary_name
        self.vocabulary_identifier = vocabulary_identifier
        self.default_language = "en"

        date_now = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S") 
        self.file_name = EXPORT_FILE_PATH %(date_now)

    def addSubElement(self, parent, elementName, text=None):
        retval = etree.SubElement(parent, self.vdexmanager.vdexTag(elementName))
        if text != None:
            retval.text = text

        return retval

    def find_record_by_priref(self, priref):
        for record in self.records:
            if record.find('priref') != None:
                if record.find('priref').text == priref:
                    return record
        return None

    def get_records_from_xml(self):
        records = etree.parse(XML_PATH).getroot().find('recordList').getchildren()
        return records

    def create_node(self, parent_priref, record):

        # get parent_priref level
        # get record details    
        details = {}
        details["termIdentifier"] = record.find('priref').text
        details["name"] = record.find('scientific_name').text
        
        # create_term in that level
        print "PARENT PRIREF: %s" %(parent_priref)
        if parent_priref != 0:
            parent = self.vdexmanager.getTermById(parent_priref)
        else:
            parent = self.vdexmanager.tree.getroot()

        if not parent:
            print "NOT PARENT"
            parent = self.vdexmanager.tree.getroot()
        
        term = self.addSubElement(parent, "term")
        termIdentifier = self.addSubElement(term, "termIdentifier", details['termIdentifier'])
        caption = self.addSubElement(term, "caption")
        langstring = self.addSubElement(caption, 'langstring', details['name'])
        langstring.attrib['language'] = self.default_language

        self.vdexmanager.makeTermDict()

        return True

    def build_tree_from_priref(self, parent_priref, priref):
        record = self.find_record_by_priref(priref)
        result = []
        
        # Go through all the childs
        # Create node from parent_priref
        if parent_priref == None:
            self.create_node(0, record)
        else:
            self.create_node(parent_priref, record)

        children = record.findall('Child')
        if len(children):
            for child in children:
                if child.find('child_name'):
                    child_priref = child.find('child_name').get('priref')
                    self.build_tree_from_priref(priref, child_priref)

        return result

    def test_run(self):
        test_priref = "8703" # Amphibia
        print "isVDEX: %s" %(self.vdexmanager.isVDEX())
        print "Number of records: %s" %(len(self.records))
        self.build_tree_from_priref(None, test_priref)
        print self.vdexmanager.serialize()
        

    def create_vdex_structure(self):
        vdex_file = open(self.file_name, "w+")

        structure = '<vdex xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.imsglobal.org/xsd/imsvdex_v1p0" language="en" orderSignificant="false" profileType="hierarchicalTokenTerms" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsvdex_v1p0 imsvdex_v1p0.xsd http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd">\n'
        structure += "<vocabIdentifier>%s</vocabIdentifier>\n" %(self.vocabulary_identifier) 
        structure += "<vocabName>%s</vocabName>\n" %(self.vocabulary_name)
        structure += "</vdex>"

        vdex_file.write(structure)
        vdex_file.close()
        return vdex_file

    def init_vdex_file(self):
        self.vdex_file = self.create_vdex_structure()

    def init(self):
        self.init_vdex_file()
        self.vdexmanager = VDEXManager(resource_stream(__name__, self.file_name))
        self.records = self.get_records_from_xml()

if __name__ == "__main__":
    vocabulary_name = "VocabularyName"
    vocabulary_identifier = "VocabularyIdentifier"
    xmltovdex = XMLtoVDEX(vocabulary_name, vocabulary_identifier)
    xmltovdex.init()
    xmltovdex.test_run()









