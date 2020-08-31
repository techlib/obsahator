#!/usr/bin/env python
# -*- coding: utf-8 -*-

# workflow processes

import os
import config
from modules import utility
from modules import catalogue
from modules import conversion
from modules import ocr
from datetime import datetime


def process_cover(info_dict, periodical=False):
    """
    Processes cover image of the document.

    First, function checks if the cover processing hasn't been done yet. If so, it returns status 'finished'.

    If the cover is not yet processed,function goes through following:

    1) Calls the functions responsible for catalogue system number search
    2) Calls the functiion responsible for converting the cover image to JPEG format
    3) Calls the function responsible for renaming the cover image file according to naming convention
    4) Calls the function responsible for moving the converted image to it's destination in shared folder
    5) Calls the function responsible for setting correct status of the document

    I one of these function fails, it raises an exception.
    :param info_dict: dict containing information about document that is currently being processed
    :param periodical: if set to True, processed cover image will be marked with "_periodical" suffix
    :return: status of the processing
    """
    if os.path.isfile(os.path.join(info_dict['path'], config.STATUS_COVER)):
        print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (COVER): Cover for document {info_dict['name']} already processed...")
        return 'finished'

    for doc_info, doc_content in info_dict.items():
        # process covers
        renamed_paths = []
        if doc_info == 'cover':
            try:
                set_number = catalogue.get_set_number(info_dict['name'])
                print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (COVER): {info_dict['name']}\tSET NUMBER: {set_number}")
                
                sysno = catalogue.get_document_sysno(set_number=set_number)
                print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (COVER): {info_dict['name']}\tSYSNO: {sysno}")
                
                converted_paths = conversion.convert_to_jpg(doc_content)
                print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (COVER): {info_dict['name']}\tCONVERTED IMAGES: {converted_paths}")
                
                if len(converted_paths) > 1:
                    raise ValueError(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR (COVER): Document {info_dict['name']} has more than one cover page.")
                
                if periodical is False:
                    for path in converted_paths:
                        new_path = utility.rename_document(original_path=path, new_name=sysno)
                        renamed_paths.append(new_path)
                    print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (COVER): {info_dict['name']}\tNEW PATHS: {renamed_paths}")

                else:
                    for path in converted_paths:
                        new_path = utility.rename_document(original_path=path, new_name=f'{sysno}_periodical')
                        renamed_paths.append(new_path)
                    print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (COVER): {info_dict['name']}\tNEW PATHS: {renamed_paths}")

                utility.copy_to_server(paths_list=renamed_paths, destination=config.COVER_DIR)
                utility.set_status(doc_path=info_dict['path'], status='cover')
                return 'finished'

            except:
                raise RuntimeError(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR (COVER): Error processing document {info_dict['name']}")


def process_toc(info_dict):
    """
    Processes images of the document's TOC pages.

    Function checks if document has any TOC pages. If it doesn't, it returns status 'finished'

    If there are any TOC pages, functions checks if they are already being processed by OCR SW. If they are,
    function check if the OCR is done. If processing is not done yet, it returns status 'running'.

    In case the OCR process is done, function checks if the OCR ended in failure or not. If it ended with failure,
    function raises an error.

    In case the OCR ended without failure, it tries to move OCR results back to the document's root directory,
    raising the exception on failure and returning the status 'finished' if it ends ok.

    In case the document is not being processed by OCR SW, function tries to move the TOC pages to OCR processing,
    call the function responsible for setting an appropriate status of the document and return the status 'running'.
    If it fails during one of these function calls, it raises an exception.

    :param info_dict: dict containing information about document that is currently being processed
    :return: status of the processing
    """

    # check if TOC can even be processed (if there are TOC pages present, if not, return 'finished')
    if len(info_dict['toc']) == 0:
        print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
              "INFO (TOC): There are no TOC pages to process for document {}...".format(info_dict['name']))
        return 'finished'

    # if document is in ocr processing,
    if os.path.isfile(os.path.join(info_dict['path'], config.STATUS_OCR)):
        print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
              "INFO (OCR): Document {} is on OCR processing...".format(info_dict['name']))
        # and it's not done, return
        if not ocr.ocr_is_done(info_dict):
            return 'running'

        # if it's done (it has result), check if is failed, if yes, raise an error
        if ocr.is_failed(info_dict):
            raise IOError(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR: Failed to OCR the document...")

        # move the finished ocr results (txt files) to document root
        try:
            ocr.move_ocr_results(info_dict)
            return 'finished'
        except IOError as e:
            raise e

    # process the document if there's no status file for OCR,
    # indicating that document was not yet sent to OCR processing
    try:
        ocr.copy_to_ocr(info_dict)
        utility.set_status(doc_path=info_dict['path'], status='ocr')
        return 'running'
    except IOError as e:
        raise e


def process_doc_monograph(doc_info_dict):
    """
    Manages the processing of the document's cover and TOC pages.

    Function tries to process the cover and TOC pages of the document and collect the status of each process. If each
    process return status 'finished', function renames the folder to mark it as DONE and sets processing status
    to 'finished'.


    If one of the processes returns different status, function sets processing status to 'running'.

    If an error occurs in one of the processes, function catches an exception, and appends the error the list.

    Finally, the function returns the document processing status and error list.

    :param doc_info_dict: dictionary containing the information about document that is currently being processed
    :return: tuple - status of the document processing and error list
    """

    errors = []
    status = ''

    try:
        cover_status = process_cover(doc_info_dict)     # process the cover
        toc_status = process_toc(doc_info_dict)         # process the TOC
        if cover_status == 'error' or toc_status == 'error':    # set the appropriate status
            status = 'error'
        elif cover_status == 'finished' and toc_status == 'finished':
            # if each process returns 'finished', rename the doc
            utility.rename_document(original_path=doc_info_dict['path'],
                                    new_name=config.FINISHED_PREFIX+doc_info_dict['name'])
            status = 'finished'                                 # set processing status to 'finished' 
        
        else:
            status = 'running'                                  # at least one of the processes returned something else
                                                                # than 'finished' or 'error'
        print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (PROCESS DOC): Status of the document {doc_info_dict['name']} is:\t{status.capitalize()}...")
    except IOError as e:
        print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR: {e} in {doc_info_dict['path']}")
        print(e)
        errors.append(e)
        status = 'error'

    finally:
        return status, errors

def process_doc_periodical(doc_info_dict):
    errors = []
    status = ''

    try:
        cover_status = process_cover(doc_info_dict, periodical=True)    # process the cover
        if cover_status == 'error':    # set the appropriate status
            status = 'error'
        elif cover_status == 'finished':
            # if each process returns 'finished', rename the doc
            utility.rename_document(original_path=doc_info_dict['path'],
                                    new_name=config.FINISHED_PREFIX+doc_info_dict['name'])
            status = 'finished'                                 # set processing status to 'finished' 
        
        else:
            status = 'running'                                  # at least one of the processes returned something else
                                                                # than 'finished' or 'error'
        print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (PROCESS DOC): Status of the document {doc_info_dict['name']} is:\t{status.capitalize()}...")
    except IOError as e:
        print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR: {e} in {doc_info_dict['path']}")
        print(e)
        errors.append(e)
        status = 'error'

    finally:
        return status, errors