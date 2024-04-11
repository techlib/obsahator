#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import config
import re
from datetime import datetime


def find_item_in_response(data, key):
    """
    Finds specified key in Ordered Dict with unknown depth.
    :param data: Ordered dict in which we are searching for the specified key
    :param key: string representing a key we're looking for
    :return: result generator
    """
    sub_iter = []
    if isinstance(data, dict):
        # if data is instance of dict
        if (key in data):
            # find key in data and yield value
            yield data[key]
        # get all values of the data structure
        sub_iter = data.values()
    if isinstance(data, list):
        # if data is instance of list, assign list the sub_iter variable
        sub_iter = data

    for x in sub_iter:
        # callback
        for y in find_item_in_response(x, key):
            yield y


def rename_document(original_path, new_name):
    """
    Renames files or directories
    :param original_path: path to the file or directory that should be renamed
    :param new_name: new name of the file or directory
    :return: path to the renamed file or directory
    """
    # get old filenames
    new_path = ''
    print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
          "INFO (UTILITY): RENAME DOCUMENT ORIGINAL PATH: ", original_path)
    # check if the path is a file or a directory
    if os.path.isfile(original_path):
        ext = os.path.splitext(original_path)[1]
        renamed = new_name + ext
        new_path = os.path.join(os.path.dirname(original_path), renamed)
    elif os.path.isdir(original_path):
        renamed = new_name
        new_path = os.path.join(os.path.dirname(original_path), renamed)
    print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
          "INFO (UTILITY): Renaming {} to {}...".format(original_path, new_path))
    # rename the file or directory
    os.rename(original_path, new_path)

    return new_path


def copy_to_server(paths_list, destination):
    """
    Copies files in a list to the destination.
    :param paths_list: list of path to the files to be copied
    :param destination: path to destination folder
    :return:
    """
    for path in paths_list:
        try:
            # check if file exists in destination folder
            if os.path.isfile(os.path.join(destination, os.path.basename(path))):
                print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                      "INFO (UTILITY): File {} already found in {}...".format(os.path.basename(path), destination))
                # skip the file is it exists in destination
                continue
            print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                  "INFO (UTILITY): Copying file {} to {}".format(path, destination))
            # copy file to it's destination
            os.system('cp ' + path + ' ' + destination) # this is working
            print("Copying: " + path + " to destination: " + destination)    
        except shutil.Error as e:
            # raise an exception if an error occurs during copying
            # print("Copying file " + os.path.basename(path) + ": " + e)
            raise IOError(f'{format(datetime.now(), "%Y-%m-%d %H:%M:%S")} ERROR(UTILITY) Cannot copy file {path} to {os.path.join(destination, os.path.basename(path))} : {e}')


def set_status(doc_path, status):
    """
    Sets status of the document processing by creating a hidden status file in the root directory of the document
    :param doc_path: path to the document directory
    :param status: status to be set
    :return: none
    """
    # creates an invisible file with name configured in config file, indicating, that cover image has already been moved
    print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO(UTILITY): DOC_PATH {doc_path}")

    filepath = doc_path
    if status == 'cover':
        filepath = os.path.join(filepath, config.STATUS_COVER)
    elif status == 'ocr':
        filepath = os.path.join(filepath, config.STATUS_OCR)
    elif status == 'finished':
        filepath = os.path.join(filepath, config.STATUS_DONE)

    print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (UTILITY): FILEPATH: {filepath}")
    try:
        f = open(filepath, mode='w')
        f.write(doc_path)
        f.close()
    except:
        raise IOError(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR (UTILITY): Failed to write the status file into {doc_path}")


def check_isbn(string):
    """
    Return true if string passed is valid isbn.
    
    :param string: string to be checked
    :return: True if checked string is valid isbn
    """
    # Drop dashes from string and convert to lowercase in case of 10 being represented as X
    string = string.replace("-", "").lower()
    
    if len(string) == 10:
        # sum of all ten digits, each multiplied by its weight in ascending order from 1 to 10, is a multiple of 11.    
        w, p = 10, 0 # weight, product
        for char in string:
            if char is not "x":
                p += int(char)*w
                w -= 1
            elif char is "x":
                p += 10*w
                w -= 1

        return p % 11 == 0 # multiple of 11 --> valid isbn-10

    
    if len(string) == 13:
        # the sum of all digits, each multiplied by its weight, alternating between 1 and 3, is a multiple of 10
        w, p = 1, 0 # weight, product
        for char in string:
            if char is not "x":
                p += int(char)*w
                w = 4-w # subtraction from their total switches between 1 and 3        
            elif char is "x":
                p += 10*w

        return p % 10 == 0 # multiple of 10 --> valid isbn-13
        
        
        
def check_issn(string):
    """
    Return true if string passed is valid issn.
    
    :param string: string to be checked
    :return: True if checked string is valid issn
    """
    # Drop dashes from string and convert to lowercase in case of 10 being represented as X
    string = string.replace("-", "").lower()

    if len(string) == 8:
        # Sum of all ten digits, each multiplied by its weight in ascending order from 1 to 8, is a multiple of 11.
        w, p = 8, 0  # weight, product
        for char in string:
            if char is not "x":
                p += int(char)*w
                w -= 1
            if char is "x":
                p += 10*w
                w -= 1

        if p % 11 == 0: # product divisble by 11 --> valid issn
            return True
        else:
            return False

def check_sysno(string):
    """
    Return true if string passed is valid NTL system number.
    In case of this workflow it always begins with SIGLA + 9 numbers    
    
    :param string: string to be checked
    :return: True if checked string is valid system number
    """
    # TODO validate if such system number exists in library catalogue as well
    # String must conform to pattern
    repattern = r'^ABA013-\d\d\d\d\d\d\d\d\d$'
    if re.match(repattern, string):
        return True


def check_cnb(string):
    """
    Return true if string passed is valid CNB identifier. 
    
    :param string: string to be checked
    :return: True if checked string is valid CNB
    """
    # TODO validate if such system number exists in library catalogue as well
    # String must conform to pattern
    repattern = r'^cnb\d\d\d\d\d\d\d\d\d$'
    if re.match(repattern, string):
        return True

def determine_identifier(string):
    repattern_cnb = r'^cnb[0-9]{9}'
    repattern_sysno = r'^ABA013-[0-9]{9}'
    repattern_isbn = r'(?:[0-9]-?){13}|(?:[0-9]-?){10}'
    repattern_issn = r'(?:[0-9]-?){8}'
    repattern_ocolc = r'\(OCoLC\)[0-9]+'

    if re.match(repattern_isbn,string) and check_isbn(string):
        return 'isbn'
    elif re.match(repattern_issn,string) and check_issn(string):
        return 'issn'
    elif re.match(repattern_cnb, string):
        return 'cnb '
    elif re.match(repattern_sysno,string):
        return 'sysno'
    elif re.match(repattern_ocolc,string):
        return 'ocolc'
    else:
        return 'fail'   