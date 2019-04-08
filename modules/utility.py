#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import config
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
        old_name, ext = os.path.splitext(original_path)
        renamed = new_name + ext
        new_path = os.path.join(os.path.dirname(original_path), renamed)
    elif os.path.isdir(original_path):
        old_name = os.path.basename(original_path)
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
            raise IOError("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                          "ERROR (UTILITY): Cannot copy file {} to {}: {}".format(path,
                                                                                  os.path.join(destination,
                                                                                               os.path.basename(path),
                                                                                               e)))


def set_status(doc_path, status):
    """
    Sets status of the document processing by creating a hidden status file in the root directory of the document
    :param doc_path: path to the document directory
    :param status: status to be set
    :return: none
    """
    # creates an invisible file with name configured in config file, indicating, that cover image has already been moved
    print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " + "INFO (UTILITY): DOC_PATH: ", doc_path)
    filepath = doc_path
    if status == 'cover':
        filepath = os.path.join(filepath, config.STATUS_COVER)
    elif status == 'ocr':
        filepath = os.path.join(filepath, config.STATUS_OCR)
    elif status == 'finished':
        filepath = os.path.join(filepath, config.STATUS_DONE)

    print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
          "INFO (UTILITY): FILEPATH: ", filepath)
    try:
        f = open(filepath, mode='w')
        f.write(doc_path)
        f.close()
    except:
        raise IOError("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                      "ERROR (UTILITY): Failed to write the status file into ", doc_path)


