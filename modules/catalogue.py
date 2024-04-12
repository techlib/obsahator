#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import config
import requests
import xmltodict
from modules import utility
import re
from datetime import datetime


def get_set_number(id_type,id_value):
    """
    Get's the set number of the document from Aleph library system based on the directory name which is equal to
    documents' isbn/issn number. Performs a search for a document record based on the identifier.
    :param dir_name: name of the
    :return: set_number: string representing a set number of the search result
    """
    # separates date and identifier from the directory name

    # TODO add request forming for issn numbers
    # construct aleph query

    code = {
        'issn' : 'SSN',
        'isbn' : 'SBN',
        'cnb'  : 'CNB'
    }


    aleph_url = config.ALEPH_API+f"?op=find&base=STK&code={code[id_type]}&request={id_value}"

    # get response
    aleph_response = requests.get(aleph_url)

    # check response from the server
    if aleph_response.status_code != 200:
        print(aleph_response.status_code, aleph_url)
        raise IOError("ERROR (CATALOGUE): Failed to retrieve set number")

    print("Aleph response: ")    
    print(aleph_response.text)

    # parse aleph response text to a dictionary
    result_set_dict = xmltodict.parse(aleph_response.text)

    # find number of records in the response
    aleph_result_generator = utility.find_item_in_response(result_set_dict, key='no_records')

    # check number of found documents
    for aleph_result in aleph_result_generator:     
        if re.match('[0]{9}', aleph_result):
            raise IOError(f"ERROR (CATALOGUE): No document found for identifier {id_value}...")
        # if there are some documents found, get the set number from the response
        if re.match('[0]{8}[1]{1}', aleph_result):
            print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (CATALOGUE): Found one result for the Aleph query.")
            set_number_generator = utility.find_item_in_response(result_set_dict, 'set_number')

            for set_number in set_number_generator:
                return set_number
        else:
            print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} WARNING (CATALOGUE): Found multiple results for search query...")
            set_number_generator = utility.find_item_in_response(result_set_dict, 'set_number')
            for set_number in set_number_generator:
                return set_number


def get_document_sysno(set_number):
    """
    Gets system number of the processed document based on the set number of the search result.
    :param set_number: string representing set number of the search result
    :return: doc_number: system number of the document
    """
    aleph_result = '000000001'  # indicates what result we want, in this case, always the first one

    print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (CATALOGUE): SET NUMBER:", set_number)

    # construct aleph record query
    aleph_record_query = config.ALEPH_API+'?op=present&set_entry='+aleph_result+'&set_number='+set_number
    # get the response from server
    aleph_record_response = requests.get(aleph_record_query)
    # check response status code
    if aleph_record_response.status_code != 200:
        print(aleph_record_response.status_code, aleph_record_query)
        raise IOError(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR (CATALOGUE): Server returned status {aleph_record_response.status_code}")

    print(aleph_record_response.status_code, aleph_record_query)
    # parse result text to a dictionary
    result_record_dict = xmltodict.parse(aleph_record_response.text)

    # search for a doc_number (sysno) in the record
    aleph_record_generator = utility.find_item_in_response(result_record_dict, key='doc_number')

    # return the doc_number (sysno)
    for doc_number in aleph_record_generator:
        print(doc_number)
        return doc_number


def catalog_lookup_sysno(id_type,id_value):
    set_no = get_set_number(id_type,id_value)
    sysno = get_document_sysno(set_no)
    return sysno


def lookup_ocolc(id_value):
    escaped = re.escape(id_value)
    ocolc_marc_regex = r"([0-9]{9}).*\$\$a"+escaped+r"(?:\$\$.*)?$"
    with open(config.ALEPH_035a_LIST_PATH,'rt') as ocolcs:
        while not ((line := ocolcs.readline()) == '' or (res := re.match(ocolc_marc_regex, line))): pass
    
    return res.group(1) if res else None

    

def resolve_id_to_sysno(id_type,id_value):
    if id_type in ['issn','isbn','cnb']:
        return catalog_lookup_sysno(id_type,id_value)
    elif id_type in ['ocolc']:
        return lookup_ocolc(id_value)
    elif id_type in ['sysno']:
        return id_value

