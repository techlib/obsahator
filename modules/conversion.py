#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
import os
from datetime import datetime

# CONVERTOR module


def convert_to_jpg(path_list):
    """
    Converts input image file to jpeg format
    :param path_list: list of paths to the image files to be converted
    :return: converted_files: list of converted files
    """
    converted_files = []
    for path in path_list:
        # get image name from path
        name = os.path.basename(path)
        dirpath = os.path.dirname(path)

        # get filename and extension from filename
        fn = os.path.splitext(name)[0]

        # construct output file name
        outfile = fn + '.jpg'

        # construct path to outfile
        outpath = os.path.join(dirpath, outfile)

        try:
            print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (CONVERSION): Converting {path} to {outpath}...")
            if path == outpath:
                print(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} INFO (CONVERSION): File {outpath} already exist, won't covert.")
                continue
            Image.open(path).save(outpath)
            converted_files.append(outpath)
        except IOError:
            raise IOError(f"{format(datetime.now(), '%Y-%m-%d %H:%M:%S')} ERROR (CONVERSION): Cannot convert {name}")

    return converted_files



