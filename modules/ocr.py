#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
import os
import xmltodict
import shutil
from datetime import datetime

from modules import utility


def is_failed(doc_dict):
    """
    Checks if OCR process ended with failure or not.
    :param doc_dict: dictionary containing information about processed document
    :return: bool - True if OCR failed, False if OCR didn't fail
    """

    results_xml = os.listdir(os.path.join(config.TOC_OCR_RESULTS, doc_dict['name']))
    print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " + "INFO (OCR): Results directory contents for {}:".format(
        os.path.join(config.TOC_OCR_RESULTS,
                     doc_dict['name'])
    ))
    print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " + "INFO (OCR): ", results_xml)
    if len(results_xml) == 0:
        raise IOError("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                      "ERROR (OCR): Result XML files not found in {}...".format(os.path.join(config.TOC_OCR_RESULTS,
                                                                                             doc_dict['name']))
        )

    for item in results_xml:
        # open XML file and parse it as an ordered dict
        print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " + "INFO (OCR): Found result file: ", item)
        print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
              "INFO (OCR): Opening result file {}...".format(os.path.join(config.TOC_OCR_RESULTS, doc_dict['name'],
                                                                          item)))
        with open(os.path.join(config.TOC_OCR_RESULTS, doc_dict['name'], item), mode='rb') as f:
            xml = xmltodict.parse(xml_input=f)
            # print("OCR XML: ", xml)

        # find XmlResult in the ordered dictionary created by parsing XML file
        result_generator = utility.find_item_in_response(data=xml, key='@IsFailed')

        # find IsFailed property in XmlResult ordered dict
        for found_value in result_generator:
            # is_failed_generator = utility.find_item_in_response(data=result, key='@IsFailed')
            #
            # # check the value of IsFailed property
            # for found_value in is_failed_generator:
            #     print("IS FAILED: ", found_value)
            if found_value == 'true':
                print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                      "INFO (OCR): TRUE RESULT FOUND VALUE: ", found_value)
                return True
            else:
                print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                      "INFO (OCR ): FALSE RESULT FOUND VALUE: ", found_value)
                return False


def ocr_is_done(doc_dict):
    """
    Check if the OCR document is done or not.
    :param doc_dict: dictionary containing the information about the document
    :return: bool - True if OCR is done, False if it's not done
    """
    print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
          "INFO (OCR): Looking for folder {}...".format(os.path.join(config.TOC_OCR_RESULTS, doc_dict['name'])))

    # check if there is an OCR result file in OCR RESULTS directory
    if not os.path.isdir(os.path.join(config.TOC_OCR_RESULTS, doc_dict['name'])):
        print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
              "INFO (OCR): There's no OCR result for {}...".format(doc_dict['name']))
        return False

    print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
          "INFO (OCR): Folder {} found in {}...".format(os.path.join(config.TOC_OCR_RESULTS, doc_dict['name']),
                                                        config.TOC_OCR_RESULTS))
    return True


def move_ocr_results(doc_dict):
    """
    Moves OCR results back to document root directory
    :param doc_dict: dictionary containing information about the document
    :return: none
    """
    # get OCR result files from OCR output directory
    result_files = os.listdir(os.path.join(config.TOC_OCR_OUT, doc_dict['name']))
    if len(result_files) == 0:
        raise IOError("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                      "ERROR (OCR): Result files not found in {}...".format(os.path.join(config.TOC_OCR_OUT,
                                                                                         doc_dict['name'])))

    for item in result_files:
        try:

            # check if does not yet exist in document root directory
            if not os.path.isfile(os.path.join(doc_dict['path'], item)):
                print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                      "INFO (OCR): Copying {} to {}".format(os.path.join(config.TOC_OCR_OUT,
                                                                         doc_dict['name'], item),
                                                            doc_dict['path']))

                # copy the output files if they are not in the document root directory
                shutil.copy2(src=os.path.join(config.TOC_OCR_OUT,doc_dict['name'], item), dst=doc_dict['path'])

            print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                  "WARNING (OCR): File {} is already in the directory {}...".format(item, doc_dict['path']))
        except:
            raise IOError("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                          "ERROR (OCR): Failed to copy result file {} to {}...".format(item, doc_dict['path']))


def copy_to_ocr(doc_dict):
    """
    Copies images to the OCR input directory
    :param doc_dict:
    :return: none
    """
    try:

        # check if document directory in OCR input directory exists
        if not os.path.exists(os.path.join(config.TOC_OCR_IN, doc_dict['name'])):
            # create missing directories
            os.makedirs(os.path.join(config.TOC_OCR_IN, doc_dict['name']))
    except:
        raise IOError("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                      "ERROR (OCR): Failed to create directory {} in {}...".format(os.path.join(config.TOC_OCR_IN,
                                                                                                doc_dict['name']),
                                                                                   config.TOC_OCR_IN))

    for item in doc_dict['toc']:

        # check if file referenced in dictionary is really in the document root directory
        if not os.path.isfile(item):

            # raise an exception if the isn't
            raise IOError("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                          "ERROR (OCR): File {} is not in the document directory {}...".format(item, doc_dict['path']))

        try:
            # copy file to document directory in OCR input directory
            shutil.copy2(src=item, dst=os.path.join(config.TOC_OCR_IN, doc_dict['name']))
        except:

            # raise exception if error occurs during copying
            raise IOError("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                          "ERROR (OCR): Failed to copy {} to {}...".format(item, os.path.join(config.TOC_OCR_IN,
                                                                                              doc_dict['name'])))
