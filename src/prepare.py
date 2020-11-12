#!.venv/bin/python
# -*- coding: utf-8 -*-

import lxml.etree as ET
import collections
import os
import urllib

from marcxml_parser import MARCXMLRecord
from marcxml_parser.record import record_iterator

from datetime import datetime

def get_marcxml_from_mets_file(path, pretty_print=False):

    namespaces = {
            'marc': 'http://www.loc.gov/MARC21/slim',
            'mets': 'http://www.loc.gov/METS/', 
            'dcterms': 'http://purl.org/dc/terms/', 
            'xlink': 'http://www.w3.org/1999/xlink', 
            'dc': 'http://purl.org/dc/elements/1.1/', 
            'fits': 'http://hul.harvard.edu/ois/xml/ns/fits/fits_output', 
            'premis': 'info:lc/xmlns/premis-v2', 
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',  
    }

    # 1. Read and parse file
    try:
        xml = ET.parse(path)
    except Exception as e:
        print("ERROR: Could not parse %s: %s" %(path, str(e)))
        return ''

    # 2. Get MARCXML from expected xpath
    record = xml.find('mets:dmdSec[@ID="marc_descriptive-"]/mets:mdWrap[@MDTYPE="MARC"]/mets:xmlData/marc:collection/marc:record', namespaces)

    return ET.tostring(record, encoding='UTF-8', pretty_print=pretty_print)

def rewrite_record_for_zaguan(rec):
    output = ''
    signature = None
    ccpb = None

    #print(rec.controlfields)

    try: 
        signature = rec.datafields["945"][0]["a"]
        signature = signature[0]
        #print("Signatura: " + signature)

    except Exception as e: 
        print("Error al obtener la signatura: %s" %(e))

    if signature:
        signature = signature.replace(" ","_")
        signature = signature.replace("-","_")
        signature = signature.replace("(","_")
        signature = signature.replace(")","")
        signature = signature.replace("__","_")

        etiq1 = collections.OrderedDict()
        etiq1['a'] = signature
        rec.add_data_field("037", " ", " ", etiq1)
        #print("Anadida etiqueta 037__a... %s" %(etiq1['a']))

        etiq2 = collections.OrderedDict()
        xmlFile = "http://biblos.unizar.es/zaguan/METS_MIGUEL/%s/METS_carga_%s.xml" %(signature, signature)
        etiq2['a'] = xmlFile
        etiq2['d'] = "Fichero METS" 
        # check if file exists...
        if (urllib.urlopen(xmlFile).getcode() != 200):
            raise IOError('ERROR: El fichero %s no existe' %xmlFile)
        else:    
            rec.add_data_field("FFT", " ", " ", etiq2)
            #print("Anadida etiqueta FFT del METS... %s" %(etiq2['a'])) 

        etiq3 = collections.OrderedDict()
        pdfFile = "http://biblos.unizar.es/zaguan/PDFS/%s.pdf" %(signature)
        thumbFile = "http://biblos.unizar.es/zaguan/thumbnails_miguel/%s.jpg" %(signature)
        etiq3['a'] = pdfFile
        etiq3['d'] = "Texto completo (PDF)" 
        etiq3['x'] = thumbFile
        print(thumbFile)
        # check if file exists...
        if (urllib.urlopen(pdfFile).getcode() != 200):
            raise IOError('ERROR: El fichero %s no existe' %pdfFile)
        elif (urllib.urlopen(thumbFile).getcode() != 200):
            raise IOError('ERROR: El fichero %s no existe' %thumbFile)
        else:
            rec.add_data_field("FFT", " ", " ", etiq3)
            #print("Anadida etiqueta FFT del PDF... %s" %(etiq3['a']))

    else:
        raise ValueError('No se encuentra signatura del registro %s' %(repr(rec.controlfields)))

    try:
        ccpb = rec.get_ctl_field('001')
        #print("CCPB: " + ccpb)
    except Exception as e:
        print("No se encuentra ccpb")
        #raise

    if ccpb:
        etiq4 = collections.OrderedDict()
        etiq4['a'] = ccpb
        rec.add_data_field("970", " ", " ", etiq4)
        #print("Anadida etiqueta 970... %s" %(etiq4['a']))

    # Remove leader
    rec.leader = None

    # Remove controlfield 001
    if '001' in rec.controlfields:
        del(rec.controlfields['001'])

    # Check 980...
    if '980' in rec.datafields:
        collection = rec.datafields["980"][0]['b']
        etiq980 = collections.OrderedDict()
        etiq980['a'] = 'FH'
        etiq980['b'] = collection
        del(rec.datafields['980'])
        rec.add_data_field("980", " ", " ", etiq980)
    else:
        raise ValueError('ERROR: No hay informacion de coleccion!')

    # get output...    
    output += rec.to_XML()

    return output

def list_input_files(rootDir):
    # Return an array containing all the input files
    output = []
    for path, _, files in os.walk(rootDir):
        for name in files:
            f = os.path.join(path, name)
            if (name != '.DS_Store'):
                output.append(f)
    return output

def main():

    output_file = './outputs/%s_marcxml_para_zaguan.xml' %datetime.isoformat(datetime.now())
    #print(os.path.realpath(__file__))
    # 1. Get all METS files
    #input_files = ['./mets_sample.xml']
    print('Listando los archivos...')
    input_files = list_input_files('./inputs/')

    # 2. For each file...
    for f in input_files:
        # 2.1 Get METS's MARC record
        print('Generando MARCXML para el input file %s' %f)
        marcxml = get_marcxml_from_mets_file(f)
        marcxml = marcxml.replace('<marc:', '<').replace('</marc:', '</')
        #print(marcxml)

        # 2.2 Create a MARCXML Object
        rec = MARCXMLRecord(xml=marcxml)

        # 2.3 Generate XML
        print('Generando el record para cargar en Zaguan...')
        output = rewrite_record_for_zaguan(rec)
        #print(output)

        # 2.4 Write XML to output
        print('Añadiendo el record en %s...' %output_file)
        fd = open(output_file, "a")
        fd.write(output)
        fd.close()

if __name__ == '__main__':
    main()