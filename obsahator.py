#!/usr/bin/env python
# -*- coding: utf-8 -*-

# OBSAHATOR
#
# is responsible for processing of the digitized cover pages and TOC pages of
# newly bought documents. Cover and TOC pages are used to enhance the document records in library OPAC.
#

import workflow
import config
import os
import re
from datetime import datetime
from modules import utility
from modules import catalogue

batch_dict = {}

# scan input folder for new documents
docs = [os.path.join(config.INPUT_DIR, d) for d in os.listdir(config.INPUT_DIR) if os.path.isdir(os.path.join(
    config.INPUT_DIR, d)) and re.match(r'^\d{8}', d)]



# check if there is any invisible file indication status of the document in each folder
for doc_path in docs:

    doc_dict = {}

    doc_dict.update({'id':      os.path.basename(doc_path)[9:],
                     'name':    os.path.basename(doc_path),
                     'path':    doc_path,
                     'toc':     [os.path.join(doc_path, f) for f in os.listdir(doc_path) if os.path.isfile(os.path.join(
                                doc_path, f)) and re.match(r'^toc-', f)],
                     'cover':   [os.path.join(doc_path, f) for f in os.listdir(doc_path) if os.path.isfile(os.path.join(
                                doc_path, f)) and re.match(r'^(?!toc-|\..*)', f)]
                                #doc_path, f)) and re.match(r'\d{1,3}', f)]  ^(?!toc-|.cover|.ocr)
                     })

    print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO starting work on th folder: {doc_dict['name']}")

    id_type, id_value = utility.determine_identifier(doc_dict['id'])

    if id_type == 'fail':
        print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR unable to determine identifier for: {doc_dict['name']}")
        utility.set_fail(doc_path, [f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR unable to determine identifier for: {doc_dict['name']}"])
        continue

    doc_dict.update({'id_type' : id_type,
                     'id_value' : id_value
                    })
    
    sysno = catalogue.resolve_id_to_sysno(id_type,id_value)
    if sysno == None:
        print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR unable to determine sysno for: {doc_dict['name']}")
        utility.set_fail(doc_path, [f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR unable to determine sysno for: {doc_dict['name']}"])
        continue

    doc_dict['sysno'] = sysno


    if doc_dict['id_type'] in ['isbn', 'cnb', 'sysno','ocolc']:
        try:
            status, errors = workflow.process_doc_monograph(doc_dict)
            doc_dict['status'] = status
            doc_dict['error'] = errors
            batch_dict[os.path.basename(doc_path)] = doc_dict   # store the document information into the batch dictionary
            print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (OBSAHATOR): Processing {doc_dict['name']} finished with {len(errors)} errors...")
            print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (OBSAHATOR): List of errors:")
            print(errors)

        except IOError as e:
            print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR (OBSAHATOR): Processing error in {doc_dict['name']} : {e}")
        print(">"*79)
    
    elif doc_dict['id_type'] in ['issn']:
        try:
            status, errors = workflow.process_doc_periodical(doc_dict)
            doc_dict['status'] = status
            doc_dict['error'] = errors
            batch_dict[os.path.basename(doc_path)] = doc_dict   # store the document information into the batch dictionary
            print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (OBSAHATOR): Processing {doc_dict['name']} finished with {len(errors)} errors...")
            print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (OBSAHATOR): List of errors:")
            print(errors)

        except IOError as e:
            print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR (OBSAHATOR): Processing error in {doc_dict['name']} : {e}")
        print(">"*79)
    
    else:
        print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR unable to determine identifier for: {doc_dict['name']}")
        utility.rename_document(original_path=doc_dict['path'],
                                new_name=config.FAIL_PREFIX+doc_dict['name'])
        print(">"*79)
        pass


